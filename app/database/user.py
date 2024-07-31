from app.models.user.user_model import UserDB

from motor.motor_asyncio import AsyncIOMotorDatabase

__db_collection = 'users'

async def get_user_by_address(
    conn: AsyncIOMotorDatabase,
    address: str
) -> UserDB | None:
    return await conn[__db_collection].find_one({"_id": address})