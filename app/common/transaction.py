from app.config import Config
from app.database.user import top_up, privilege_user_minecraft

from decimal import Decimal

import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase

privilege_mapper = {
    0: "tourist",
    100: "worker",
    500: "citizen",
    1000: "aristocrat",
    5000: "apostle"
}


async def get_last_transactions(
        db: AsyncIOMotorDatabase, 
        our_wallet: str, 
        jetton_master_address: str, 
        token_symbol: str
    ):
    url = f"https://tonapi.io/v2/accounts/{our_wallet}/jettons/{jetton_master_address}/history?limit=100&key={Config.TON_API_KEY}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=5)
    data = response.json()
    transactions = data["events"]
    completed_transactions = []
    for transaction in transactions:
        if transaction['in_progress']: #Только завершенные транзакции
            continue #Пропускаем транзакции, которые не завершены
        for action in transaction['actions']:
            if action["type"] == "JettonTransfer" and action["status"] == "ok": #Только успешные переводы
                action = action["JettonTransfer"]
                if action["recipient"]['address'] == our_wallet: #Наш кошелек
                    if action['jetton']['address'] != jetton_master_address: #Проверка на адрес токена
                        continue
                    if action['jetton']['symbol'] != token_symbol: #Проверка на символ токена
                        continue
                    amount = Decimal(action["amount"])/(10**action['jetton']['decimals'])
                    user_address = action["sender"]["address"]
                    if action["comment"] == "Top up":
                        await top_up(db, user_address, amount)
                    elif action["comment"] == "Privilege":
                        # TODO: redo mapper when rank costs will be known
                        privilege = privilege_mapper(int(amount))
                        await privilege_user_minecraft(db, user_address, privilege)
                    completed_transactions.append({
                                                    # "comment_id": comment_id, 
                                                   "amount": amount, 
                                                   "transaction": transaction['event_id'], 
                                                   "sender_wallet": action["sender"]['address'],
                                                   "timestamp": transaction['timestamp'], 
                                                })
    return completed_transactions
