from pydantic import BaseModel

class ConclusionRequest(BaseModel):
    amount: float