from pydantic import BaseModel

from decimal import Decimal


class MoneyTransferRequest(BaseModel):
    sender_name: str
    recipient_name: str
    amount: Decimal
