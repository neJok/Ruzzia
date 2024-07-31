from pydantic import BaseModel


class TokenData(BaseModel):
    address: str | None = None

class TokensResponse(BaseModel):
    access_token: str
    refresh_token: str
    tokens_type: str