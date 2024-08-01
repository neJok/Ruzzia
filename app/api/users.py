import hmac
import time

from fastapi import APIRouter, Depends
from nacl.utils import random
from base64 import b64decode
from hashlib import sha256
from nacl.signing import VerifyKey
from nacl.encoding import HexEncoder
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import timedelta

from app.models.user.connect_wallet import ConnectWalletRequest, PayloadResponse
from app.database.user import get_user_by_address, create_user
from app.database.mongo import get_db
from app.common.error import BadRequest
from app.common.ton_api import get_data_by_state_init
from app.common.jwt import create_access_token, create_refresh_token, get_current_user
from app.common.nft import check_user_existance_in_presale_table
from app.config import Config
from app.models.user.token import TokensResponse
from app.models.user.user_model import UserDB
from app.models.user.nft_presence import NftPresenceResponse

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
async def connect(wallet: ConnectWalletRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    payload_bytes = bytes.fromhex(wallet.proof.payload)
    if len(payload_bytes) != 32:
        raise BadRequest([f"Invalid payload length, got {len(payload_bytes)}, expected 32"])
    
    mac = hmac.new(Config.app_settings['ton_connect_secret'].encode(), payload_bytes[:16], sha256)
    payload_signature_bytes = mac.digest()

    if not payload_bytes[16:] == payload_signature_bytes[:16]:
        raise BadRequest(["Invalid payload signature"])
    
    now = int(time.time())

    expire_bytes = payload_bytes[8:16]
    expire_time = int.from_bytes(expire_bytes, "big")
    if now > expire_time:
        raise BadRequest(["Payload expired"])
    
    if now > wallet.proof.timestamp + Config.app_settings['proof_ttl']:
        raise BadRequest(["TON proof has expired"])

    # TODO: Set site domain in production
    """ if wallet.proof.domain != "":
        raise BadRequest([f"Wrong domain, got {wallet.proof.domain}, expected {DOMAIN}"]) """
    
    if wallet.proof.domain.lengthBytes != len(wallet.proof.domain.value):
        raise BadRequest([f"Domain length mismatched against provided length bytes of {wallet.proof.domain.value}"])
    
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

    address, public_key = await get_data_by_state_init(wallet.state_init)
    if address != wallet.address:
        raise BadRequest(["Invalid state init"])

    try:
        verify_key = VerifyKey(public_key, HexEncoder)
        verify_key.verify(sha256(signature_message).digest(), b64decode(wallet.proof.signature))
    except:
        raise BadRequest(["Invalid payload signature"])
    
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

@router.post('/nft_presence', response_model=NftPresenceResponse, status_code=200, summary='User verification of nft presence', responses={400: {}})
async def nft_presence(user: UserDB = Depends(get_current_user)):
    user_wallet_address = user.id
    return NftPresenceResponse(presence=check_user_existance_in_presale_table(user_wallet_address))