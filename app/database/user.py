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
            "discord": {
                "id": None,
                "state": None,
            },
            "minecraft": {
                "name": None,
            }
        }
    )

async def update_user_discord_state(
    conn: AsyncIOMotorDatabase,
    user_id: str,
    state: str,
):
    await conn[__db_collection].update_one(
        {"_id": user_id},
        {"$set": {"discord.state": state}}
    )

async def update_user_discord_id(
    conn: AsyncIOMotorDatabase,
    state: str,
    discord_id: int
):
    await conn[__db_collection].update_one(
        {"discord.state": state, "discord.id": None},
        {"$set": {"discord.id": discord_id}}
    )

async def update_user_minecraft_name(
    conn: AsyncIOMotorDatabase,
    id: str,
    name: str
):
    await conn[__db_collection].update_one(
        {"_id": id},
        {"$set": {"minecraft.name": name}}
    )