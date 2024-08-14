from pydantic import BaseModel

from datetime import datetime
from typing import Literal

from app.models.mongo_model import MongoModel


class TransactionHistoryBase(BaseModel):
    user_id: str
    status: Literal["top up", "withdraw", "in-game transfer"]
    amount: float


class TransactionHistoryDB(TransactionHistoryBase, MongoModel):
    id: str
    created_at: datetime
