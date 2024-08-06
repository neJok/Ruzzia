import aiohttp
import httpx

from decimal import Decimal
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import Config
from app.database.user import top_up, privilege_user_minecraft, get_user_by_address
from app.common.discord_api import add_role_to_user, remove_role_from_user, send_message_to_logs


async def get_data_by_state_init(state_init: str):
    """Get address, public key by state init"""

    url = 'https://tonapi.io/v2/tonconnect/stateinit'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        "state_init": state_init
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            result = await response.json()
            return result['address'], result['public_key']
        

async def get_last_transactions(
        db: AsyncIOMotorDatabase, 
        our_wallet: str, 
        jetton_master_address: str, 
        token_symbol: str
    ):
    url = f"https://tonapi.io/v2/accounts/{our_wallet}/jettons/{jetton_master_address}/history?limit=100&key={Config.app_settings['ton_api_key']}"
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

                    user = await get_user_by_address(db, user_address)
                    if not user:
                        continue
                    
                    if action["comment"] == "Top up":
                        await top_up(db, user_address, amount)
                    elif action["comment"] == "Rank":
                        # TODO: redo mapper when rank costs will be known
                        privilege = Config.privilege_mapper(int(amount))
                        await privilege_user_minecraft(db, user_address, privilege)

                        if user.discord.id:
                            if user.minecraft.privilege:
                                privilege_role = Config.privilege_roles(user.minecraft.privilege)
                                await remove_role_from_user(user.discord.id, privilege_role)
                                await send_message_to_logs(f"У пользователя <@{user.discord.id}> снята роль привелегии <@&{privilege_role}>")
                            
                            privilege_role = Config.privilege_roles(privilege)
                            await add_role_to_user(user.discord.id, privilege_role)
                            await send_message_to_logs(f"Пользователю <@{user.discord.id}> выдана роль привелегии <@&{privilege_role}>")
                        
                    completed_transactions.append({
                        # "comment_id": comment_id, 
                        "amount": amount, 
                        "transaction": transaction['event_id'], 
                        "sender_wallet": action["sender"]['address'],
                        "timestamp": transaction['timestamp'], 
                    })
                    
    return completed_transactions