import aiohttp

from decimal import Decimal
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import Config
from app.database.user import top_up, privilege_user_minecraft, get_user_by_address, add_transaction
from app.common.discord_api import add_role_to_user, remove_role_from_user, send_message_to_logs
from pytoniq_core import Address

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
    ):
    url = f"https://tonapi.io/v2/accounts/{Config.app_settings['our_wallet']}/jettons/{Config.app_settings['jetton_master_address']}/history?limit=100"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

            transactions = data["events"]
            for transaction in transactions:
                if transaction['in_progress']: #Только завершенные транзакции
                    continue #Пропускаем транзакции, которые не завершены
                for action in transaction['actions']:
                    if action["type"] == "JettonTransfer" and action["status"] == "ok": #Только успешные переводы
                        action = action["JettonTransfer"]
                        if action["recipient"]['address'] == Address(Config.app_settings['our_wallet']).to_str(is_user_friendly=False): #Наш кошелек
                            if action['jetton']['address'] != Address(Config.app_settings['jetton_master_address']).to_str(is_user_friendly=False): #Проверка на адрес токена
                                continue
                            if action['jetton']['symbol'] != Config.app_settings['token_symbol']: #Проверка на символ токена
                                continue

                            amount = Decimal(action["amount"])/(10**action['jetton']['decimals'])
                            user_address = str(action["sender"]["address"])

                            user = await get_user_by_address(db, str(user_address))
                            if not user or transaction['event_id'] in user.completed_transactions:
                                continue

                            await add_transaction(db, user_address, transaction['event_id'])
                            
                            if action["comment"] == "Top up":
                                await top_up(db, user_address, float(amount))
                            elif action["comment"] == "Privilege":
                                # TODO: redo mapper when privilege costs will be known
                                privilege = Config.privilege_mapper[int(amount)]
                                await privilege_user_minecraft(db, user_address, privilege)
                                
                                try:
                                    if user.discord.id and user.minecraft.privilege != privilege:
                                        if user.minecraft.privilege:
                                            privilege_role = Config.privilege_roles[user.minecraft.privilege]
                                            await remove_role_from_user(user.discord.id, privilege_role)
                                            await send_message_to_logs(f"У пользователя <@{user.discord.id}> снята роль привелегии <@&{privilege_role}>")
                                        
                                        privilege_role = Config.privilege_roles[privilege]
                                        await add_role_to_user(user.discord.id, privilege_role)
                                        await send_message_to_logs(f"Пользователю <@{user.discord.id}> выдана роль привелегии <@&{privilege_role}>")
                                except:
                                    continue