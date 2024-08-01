from pydantic import BaseModel


class NftPresenceResponse(BaseModel):
    presence: bool