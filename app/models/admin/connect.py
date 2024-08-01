from pydantic import BaseModel

class MinecraftUserInfo(BaseModel):
    name: str
    token: str