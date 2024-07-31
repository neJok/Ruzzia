from pydantic import BaseModel, constr

from datetime import datetime

from app.models.mongo_model import MongoModel


class UserBase(BaseModel):
    balance: float


class UserDB(UserBase, MongoModel):
    id: str
    created_at: datetime