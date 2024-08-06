from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.common.admin import check_admin_token
from app.common.error import BadRequest
from app.common.jwt import decode_minecraft_token
from app.database.mongo import get_db
from app.database.user import (get_user_by_address, update_user_minecraft_name, 
                               get_user_by_minecraft_name, get_user_by_discord_id,
                               has_sufficient_funds, make_transfer)
from app.models.admin.connect import MinecraftUserInfo
from app.models.user.user_model import UserDB
from app.models.admin.money_transfer import MoneyTransferRequest


router = APIRouter(
    dependencies=[Depends(check_admin_token)]
)


@router.post('/minecraft/connect', summary='Connect minecraft account', response_model=UserDB, responses={400: {}})
async def connect(user_info: MinecraftUserInfo, db: AsyncIOMotorDatabase = Depends(get_db)):
    address = await decode_minecraft_token(user_info.token)
    if not address:
        raise BadRequest(['Не удается валидировать токен доступа'])

    user = await get_user_by_address(db, address)
    if not user:
        raise BadRequest(['Пользователь не найден'])

    if user.minecraft.name:
        raise BadRequest(['Майнкрафт уже подключен к данному аккаунту'])
    
    if await get_user_by_minecraft_name(db, user_info.name):
        raise BadRequest(['Этот аккаунт уже привязан к другому кошельку'])
    
    user.minecraft.name = user_info.name
    
    await update_user_minecraft_name(db, user.id, user_info.name)
    return user

@router.get('/minecraft/user', summary='Get user by name', response_model=UserDB, responses={400: {}})
async def get_user_by_name(name: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = await get_user_by_minecraft_name(db, name)
    if not user:
        raise BadRequest(['Пользователь не найден'])
    
    return user
    
@router.get('/discord/user', summary='Get user by discord id', response_model=UserDB, responses={400: {}})
async def get_user_by_id(discord_id: int, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = await get_user_by_discord_id(db, discord_id)
    if not user:
        raise BadRequest(['Пользователь не найден'])
    
    return user


@router.post('/minecraft/money-transfer', status_code=200, summary="Transfer money from one user to another", responses={400: {}})
async def money_transfer(transfer_data: MoneyTransferRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    if transfer_data.sender_name == transfer_data.recipient_name:
        raise BadRequest(['Никнеймы отправителя и получателя должны отличаться'])
    
    sender = await get_user_by_minecraft_name(db, transfer_data.sender_name)
    recipient = await get_user_by_minecraft_name(db, transfer_data.recipient_name)
    if not sender:
        raise BadRequest(['Отправитель не найден'])
    
    if not recipient:
        raise BadRequest(['Получатель не найден'])
    
    if not await has_sufficient_funds(db, transfer_data.sender_name, transfer_data.amount):
        raise BadRequest(['У отправителя недостаточно средств'])
    
    await make_transfer(db, transfer_data.sender_name, 
                        transfer_data.recipient_name, transfer_data.amount)
