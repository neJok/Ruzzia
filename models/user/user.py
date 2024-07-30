from pydantic import BaseModel, constr
from datetime import datetime

from models.mongo_model import MongoModel


class UserBase(BaseModel):
    name: constr(max_length=255)


class UserDB(UserBase, MongoModel):
    id: str
    create_time: datetime