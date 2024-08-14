from motor.motor_asyncio import AsyncIOMotorDatabase

from datetime import datetime
from typing import Literal


__db_collection = 'transactions_history'

async def create_transaction_history(
    conn: AsyncIOMotorDatabase,
    transaction_id: str,
    sender: str,
    recipient: str,
    status: Literal["top up", "withdraw", "in-game transfer"],
    amount: float
):
    await conn[__db_collection].insert_one(
        {
            "_id": transaction_id,
            "created_at": datetime.now(),
            "sender": sender,
            "recipient": recipient,
            "status": status,
            "amount": amount
        }
    )
