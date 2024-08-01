from typing import Optional
from pydantic import BaseModel, constr

from datetime import datetime

from app.models.mongo_model import MongoModel

class UserDiscord(BaseModel):
    id: Optional[int] = None
    state: Optional[str] = None

class UserBase(BaseModel):
    balance: float
    discord: UserDiscord


class UserDB(UserBase, MongoModel):
    id: str
    created_at: datetime