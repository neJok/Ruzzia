from pydantic import BaseModel


class QueueStatusResponse(BaseModel):
    user_position: int
