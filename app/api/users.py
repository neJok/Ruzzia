import hmac
import time
import asyncio

from random import choices
from string import ascii_letters, digits
from typing import Optional
from fastapi import APIRouter, Cookie, Depends, Request
from fastapi.responses import RedirectResponse
from nacl.utils import random
from base64 import b64decode
from hashlib import sha256
from nacl.signing import VerifyKey
from nacl.encoding import HexEncoder
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis
from datetime import timedelta

from app.config import Config
from app.database.user import get_user_by_address, create_user, update_user_discord_id, update_user_discord_state, get_user_by_discord_id, inc_balance
from app.database.mongo import get_db
from app.redis.redis import get_redis
from app.redis.user import left_get_position_in_queue, right_add_to_queue, left_remove_from_queue
from app.common.error import BadRequest
from app.common.ton_api import get_data_by_state_init
from app.common.discord_api import get_user_discord_id, authorize_discord
from app.common.jwt import create_access_token, create_refresh_token, get_current_user, decode_access_token, create_minecraft_token
from app.common.nft import check_user_existance_in_presale_table
from app.common.litebalancer import send_tokens_to_address
from app.models.user.conclusion import ConclusionRequest
from app.models.user.connect_wallet import ConnectWalletRequest, PayloadResponse
from app.models.user.token import TokensResponse
from app.models.user.user_model import UserDB
from app.models.user.nft_presence import NftPresenceResponse
from app.models.user.connect_minecraft import MinecraftTokenReponse
from app.models.user.registration_queue import QueueStatusResponse


router = APIRouter()


@router.get('/payload', response_model=PayloadResponse, status_code=200, summary='Get ton connect payload')
async def payload():
    random_bits = random(8)
    current_time = int(time.time())
    expiration_time = current_time + Config.app_settings['payload_ttl']
    expiration_time_bytes = expiration_time.to_bytes(8, 'big')
    payload = random_bits + expiration_time_bytes
    hmac_instance = hmac.new(Config.app_settings['ton_connect_secret'].encode(), payload, sha256)
    signature = hmac_instance.digest()
    final_payload = payload + signature
    payload_hex = final_payload[:32].hex()
    
    return PayloadResponse(payload=payload_hex)


@router.post('/connect', response_model=TokensResponse, status_code=200, summary='Ton connect', responses={400: {}})
async def connect(wallet: ConnectWalletRequest, db: AsyncIOMotorDatabase = Depends(get_db), r: Redis = Depends(get_redis)):
    payload_bytes = bytes.fromhex(wallet.proof.payload)
    if len(payload_bytes) != 32:
        raise BadRequest([f"Неверная длина полезной нагрузки, полученно {len(payload_bytes)}, ожидалось 32"])
    
    mac = hmac.new(Config.app_settings['ton_connect_secret'].encode(), payload_bytes[:16], sha256)
    payload_signature_bytes = mac.digest()

    if not payload_bytes[16:] == payload_signature_bytes[:16]:
        raise BadRequest(["Неверная сигнатура полезной нагрузки"])
    
    now = int(time.time())

    expire_bytes = payload_bytes[8:16]
    expire_time = int.from_bytes(expire_bytes, "big")
    if now > expire_time:
        raise BadRequest(["Истек срок действия полезной нагрузки"])
    
    if now > wallet.proof.timestamp + Config.app_settings['proof_ttl']:
        raise BadRequest(["Истёк срок действия TON proof"])

    # TODO: Set site domain in production
    """ if wallet.proof.domain != "":
        raise BadRequest([f"Wrong domain, got {wallet.proof.domain}, expected {DOMAIN}"]) """
    
    if wallet.proof.domain.lengthBytes != len(wallet.proof.domain.value):
        raise BadRequest([f"Длина домена не совпадает с длиной полученных байтов: {wallet.proof.domain.value}"])
    
    wc, whash = wallet.address.split(':', maxsplit=2)

    message = bytearray()
    message.extend('ton-proof-item-v2/'.encode())
    message.extend(int(wc, 10).to_bytes(4, 'little'))
    message.extend(bytes.fromhex(whash))
    message.extend(wallet.proof.domain.lengthBytes.to_bytes(4, 'little'))
    message.extend(wallet.proof.domain.value.encode())
    message.extend(wallet.proof.timestamp.to_bytes(8, 'little'))
    message.extend(wallet.proof.payload.encode())

    signature_message = bytearray()
    signature_message.extend(bytes.fromhex('ffff'))
    signature_message.extend('ton-connect'.encode())
    signature_message.extend(sha256(message).digest())

    await right_add_to_queue(r, wallet.address)

    address, public_key = await get_data_by_state_init(wallet.state_init)
    if address != wallet.address:
        raise BadRequest(["Невалидное состояние инициализации"])

    try:
        verify_key = VerifyKey(public_key, HexEncoder)
        verify_key.verify(sha256(signature_message).digest(), b64decode(wallet.proof.signature))
    except:
        raise BadRequest(["Невалидная сигнатура полезной нагрузки"])
    
    # await left_remove_from_queue(r)
    
    user = await get_user_by_address(db, wallet.address)
    if not user:
        await create_user(db, wallet.address)

    access_token_expires = timedelta(minutes=Config.app_settings['access_token_expire_minutes'])
    access_token = create_access_token(
        data={"sub": wallet.address}, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(minutes=Config.app_settings['refresh_token_expire_minutes'])
    refresh_token = create_refresh_token(
        data={"sub": wallet.address}, expires_delta=refresh_token_expires
    )
    
    return TokensResponse(access_token=access_token, refresh_token=refresh_token, tokens_type="Bearer")

@router.post('/', response_model=UserDB, status_code=200, summary='Get user info')
async def get_user_info(user: UserDB = Depends(get_current_user)):
    return user

@router.post('/nft-presence', response_model=NftPresenceResponse, status_code=200, summary='User verification of nft presence', responses={400: {}})
async def nft_presence(user: UserDB = Depends(get_current_user)):
    user_wallet_address = user.id
    return NftPresenceResponse(presence=check_user_existance_in_presale_table(user_wallet_address))

@router.get('/discord', status_code=200, include_in_schema=False)
async def discord_oauth2(access_token: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    address = await decode_access_token(access_token)
    if not address:
        raise BadRequest(['Не удается валидировать токен доступа'])

    user = await get_user_by_address(db, address)
    if not user:
        raise BadRequest(['Пользователь не найден'])

    if user.discord.id is not None:
        raise BadRequest(['Дискорд уже подключен к данному аккаунту'])

    state = sha256(''.join(choices(ascii_letters + digits, k=16)).encode()).hexdigest()
    await update_user_discord_state(db, user.id, state)
    
    response = RedirectResponse(f"https://discord.com/api/oauth2/authorize?client_id={Config.app_settings['discord_client_id']}&redirect_uri={Config.app_settings['discord_redirect_uri']}&response_type=code&scope=identify&state={state}")
    response.set_cookie(key="oauth_state", value=state, httponly=True)
    return response

@router.get('/discord-callback', status_code=200, include_in_schema=False)
async def discord_oauth2_callback(request: Request, oauth_state: Optional[str] = Cookie(None), db: AsyncIOMotorDatabase = Depends(get_db)):
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if not code or not state:
        raise BadRequest(['Авторизационный "code" либо "state" не были получены'])
    
    if state != oauth_state:
        raise BadRequest(["Невалидное состояние"])

    response = RedirectResponse(url="/")
    response.delete_cookie(key="oauth_state")
    
    try:
        access_token = await authorize_discord(code)
    except:
        raise BadRequest(["Не удалось получить токен доступа"])

    try:
        user_id = await get_user_discord_id(access_token)
    except:
        raise BadRequest(["Не удалось получить информацию о пользователе"])
    
    if await get_user_by_discord_id(db, user_id):
        raise BadRequest(["Этот аккаунт уже привязан к другому кошельку"])
    
    await update_user_discord_id(db, state, user_id)
    return RedirectResponse(Config.app_settings['frontend_uri'])
    

@router.get('/minecraft', status_code=200, response_model=MinecraftTokenReponse, summary="Create minecraft connect token", responses={400: {}})
async def minecraft_connect(user: UserDB = Depends(get_current_user)):
    if user.minecraft.name:
        raise BadRequest(['Майнкрафт уже подключен к данному аккаунту'])
    
    minecraft_token_expires = timedelta(minutes=Config.app_settings['access_token_expire_minutes'])
    minecraft_token = create_minecraft_token(
        data={"sub": user.id}, expires_delta=minecraft_token_expires
    )
    return MinecraftTokenReponse(token=minecraft_token)

@router.post('/conclusion', status_code=200, summary="Withdraw the balance", responses={400: {}})
async def create_conclusion(conclusion: ConclusionRequest, user: UserDB = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    if conclusion.amount <= 0:
        raise BadRequest(['Сумма вывода должна быть больше 0'])
    
    if user.balance < conclusion.amount:
        raise BadRequest(['У вас не хватает средств на кошельке'])
    
    await inc_balance(db, user.id, -conclusion.amount)

<<<<<<< HEAD
    await send_tokens_to_address(user.id, conclusion.amount)


@router.get('/queue-status', status_code=200, response_model=QueueStatusResponse, summary="Get registration queue status", responses={400: {}})
async def get_queue_status(user: UserDB = Depends(get_current_user), r: Redis = Depends(get_redis)):
    user_position = await left_get_position_in_queue(r, user.id)
    if user_position is None:
        raise BadRequest(['Пользователя нет в очереди'])
    
    return QueueStatusResponse(user_position=user_position)
=======
    try:
        await send_tokens_to_address(db, user.id, conclusion.amount)
    except:
        return BadRequest(["Не получилось вывести средства, попробуйте позже"])
>>>>>>> b1e2909aa8ce8e62dfd9fb4448eb12ba4409babd
