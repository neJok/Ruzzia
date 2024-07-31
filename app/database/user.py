from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime

from app.models.user.user_model import UserDB


__db_collection = 'users'

async def get_user_by_address(
    conn: AsyncIOMotorDatabase,
    address: str
) -> UserDB | None:
    user = await conn[__db_collection].find_one({"_id": address})
    if user is None:
        return None
    
    user['id'] = user.pop('_id')
    return UserDB(**user)

async def create_user(
    conn: AsyncIOMotorDatabase,
    address: str
):
    await conn[__db_collection].insert_one(
        {
            "_id": address, 
            "created_at": datetime.now(),
            "balance": 0,
        }
    )