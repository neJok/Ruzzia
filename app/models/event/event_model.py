from datetime import time, datetime

from pydantic import BaseModel


class EventBase(BaseModel):
    name: str
    start_time: datetime
