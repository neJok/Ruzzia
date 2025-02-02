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

async def get_user_by_minecraft_name(
    conn: AsyncIOMotorDatabase,
    name: str
) -> UserDB | None:
    user = await conn[__db_collection].find_one({"minecraft.name": name})
    if user is None:
        return None
    
    user['id'] = user.pop('_id')
    return UserDB(**user)

async def get_user_by_discord_id(
    conn: AsyncIOMotorDatabase,
    discord_id: int
) -> UserDB | None:
    user = await conn[__db_collection].find_one({"discord.id": discord_id})
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
                "privilege": "tourist",
            },
            "completed_transactions": []
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


async def make_transfer(
    conn: AsyncIOMotorDatabase,
    sender_name: str,
    recipient_name: str,
    amount: float
):
    await conn[__db_collection].update_one(
        {'minecraft.name': sender_name},
        {"$inc": {"balance": -amount}}
    )
    await conn[__db_collection].update_one(
        {'minecraft.name': recipient_name},
        {"$inc": {"balance": amount}}
    )


async def get_balances_after_transaction(
    conn: AsyncIOMotorDatabase,
    sender_name: str,
    recipient_name: str
):
    sender = await get_user_by_minecraft_name(conn, sender_name)
    recipient = await get_user_by_minecraft_name(conn, recipient_name)
    sender_balance_after_transaction = sender.balance
    recipient_balance_after_transaction = recipient.balance
    return sender_balance_after_transaction, recipient_balance_after_transaction


async def has_sufficient_funds(
    conn: AsyncIOMotorDatabase, 
    sender_name: str, 
    amount: float
):
    sender = await conn[__db_collection].find_one({'minecraft.name': sender_name})
    sender_balance = sender['balance']
    return sender_balance >= amount


async def inc_balance(
    conn: AsyncIOMotorDatabase,
    user_address: str,
    amount: float
):
    await conn[__db_collection].update_one(
        {"_id": user_address},
        {"$inc": {"balance": amount}}
    )


async def privilege_user_minecraft(
    conn: AsyncIOMotorDatabase,
    user_address: str,
    privilege: str
):
    await conn[__db_collection].update_one(
        {"_id": user_address},
        {"$set": {"minecraft.privilege": privilege}}
    )

async def add_transaction(
    conn: AsyncIOMotorDatabase,
    user_address: str,
    transaction_id: str
):
    await conn[__db_collection].update_one(
        {"_id": user_address},
        {"$push": {"completed_transactions": transaction_id}}
    )