import asyncio

from decimal import Decimal
from pytoniq_core import Address

from app.config import Config
from app.database.mongo import connect_and_init_db, get_db
from app.redis.redis import connect_and_init_redis
from app.common.ton_api import get_last_transactions
from app.database.user import inc_balance, privilege_user_minecraft, get_user_by_address, add_transaction
from app.database.transaction_history import create_transaction_history
from app.common.discord_api import add_role_to_user, remove_role_from_user, send_message_to_logs

async def check_trasactions_task():
    db = await get_db()

    while True:
        data = await get_last_transactions(Config.app_settings['our_wallet'])

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
                        await create_transaction_history(
                            db, transaction['event_id'], user_address,
                            Address(Config.app_settings['jetton_master_address']).to_str(is_user_friendly=False), 
                            "top up", amount
                        )
                        
                        if action["comment"] == "Top up":
                            await inc_balance(db, user_address, float(amount))
                        elif action["comment"] == "Privilege":
                            # TODO: redo mapper when privilege costs will be known
                            privilege = Config.privilege_mapper[int(amount)]
                            await privilege_user_minecraft(db, user_address, privilege)
                            
                            try:
                                if user.discord.id and user.minecraft.privilege != privilege:
                                    old_privilege_role = Config.privilege_roles[user.minecraft.privilege]
                                    await remove_role_from_user(user.discord.id, old_privilege_role)
                                    
                                    new_privilege_role = Config.privilege_roles[privilege]
                                    await add_role_to_user(user.discord.id, new_privilege_role)
                                    
                                    await send_message_to_logs(f"Пользователь <@{user.discord.id}> сменил привилегию с <@&{old_privilege_role}> на <@&{new_privilege_role}>")
                            except:
                                continue

        await asyncio.sleep(10)

async def startup():
    await connect_and_init_db()
    await connect_and_init_redis()
    asyncio.create_task(check_trasactions_task())
