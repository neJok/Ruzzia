from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.common.admin import check_admin_token
from app.common.error import BadRequest
from app.common.jwt import decode_minecraft_token
from app.database.mongo import get_db
from app.database.user import get_user_by_address, update_user_minecraft_name
from app.models.admin.connect import MinecraftUserInfo
from app.models.user.user_model import UserDB


router = APIRouter(
    dependencies=[Depends(check_admin_token)]
)


@router.post('/minecraft/connect', summary='Connect minecraft account', response_model=UserDB, responses={400: {}})
async def connect(user_info: MinecraftUserInfo, db: AsyncIOMotorDatabase = Depends(get_db)):
    address = await decode_minecraft_token(user_info.token)
    if not address:
        raise BadRequest(['Could not validate access token'])

    user = await get_user_by_address(db, address)
    if not user:
        raise BadRequest(['User not found'])

    if user.minecraft.name:
        raise BadRequest(['You already have a minecraft connected'])
    
    user.minecraft.name = user_info.name
    
    await update_user_minecraft_name(db, user.id, user_info.name)
    return user
    