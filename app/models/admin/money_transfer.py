from pydantic import BaseModel


class MoneyTransferRequest(BaseModel):
    sender_name: str
    recipient_name: str
    amount: float


class MoneyTransferResponse(BaseModel):
    sender_balance_after_transaction: float
    recipient_balance_after_transaction: float
