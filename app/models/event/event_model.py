from datetime import time, datetime

from pydantic import BaseModel


class EventBase(BaseModel):
    name: str
    start_time: time
    expire_at: datetime


class EventResponse(BaseModel):
    name: str
    start_time: time
