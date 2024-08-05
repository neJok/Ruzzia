from pydantic import BaseModel


class MoneyTransferRequest(BaseModel):
    sender_name: str
    recipient_name: str
    amount: int
