import asyncio
from datetime import datetime

from pytoniq import LiteBalancer, WalletV4R2, begin_cell
from pytoniq_core import Address
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import Config
from app.database.transaction_history import create_transaction_history
from app.database.user import inc_balance
from app.common.ton_api import get_last_transactions


async def send_tokens_to_address(db: AsyncIOMotorDatabase, destination_address: str, amount: float):
    provider = LiteBalancer.from_mainnet_config(1)
    await provider.start_up()

    wallet = await WalletV4R2.from_mnemonic(provider=provider, mnemonics=Config.app_settings['our_wallet_mnemonics'].split(' '))
    USER_ADDRESS = wallet.address

    USER_JETTON_WALLET = (await provider.run_get_method(address=Address(Config.app_settings['jetton_master_address']).to_str(is_user_friendly=True, is_bounceable=True, is_url_safe=True),
                                                        method="get_wallet_address",
                                                        stack=[begin_cell().store_address(USER_ADDRESS).end_cell().begin_parse()]))[0].load_address()
    
    DESTINATION_ADDRESS_FRINEDLY = Address(destination_address).to_str(is_user_friendly=True, is_bounceable=True, is_url_safe=True)
    forward_payload = (begin_cell()
                      .store_uint(0, 32)
                      .store_snake_string("Conclusion | ruzzia.org")
                      .end_cell())
    transfer_cell = (begin_cell()
                    .store_uint(0xf8a7ea5, 32)
                    .store_uint(0, 64)
                    .store_coins(int(amount * 10**9))
                    .store_address(DESTINATION_ADDRESS_FRINEDLY)
                    .store_address(USER_ADDRESS)
                    .store_bit(0)
                    .store_coins(1)
                    .store_bit(1)
                    .store_ref(forward_payload)
                    .end_cell())
    
    await wallet.transfer(destination=USER_JETTON_WALLET, amount=int(0.05 * 1e9), body=transfer_cell) 
    await provider.close_all()
    
    create_transaction_date = datetime.now()
    
    transaction_id = None
    attempts = 0
    while transaction_id is None and attempts < 10:
        await asyncio.sleep(120)
        attempts += 1

        user_transactions_data = await get_last_transactions(destination_address)
        transactions = user_transactions_data["events"]
        for transaction in transactions:
            given_date = datetime.fromtimestamp(transaction['timestamp'])
            if given_date < create_transaction_date:
                break

            if transaction['in_progress']:
                continue

            for action in transaction['actions']:
                if action["type"] == "JettonTransfer" and action["status"] == "ok":
                    action = action["JettonTransfer"]
                    if action["recipient"]['address'] == destination_address and action["sender"]['address'] == Address(Config.app_settings['our_wallet']).to_str(is_user_friendly=False):
                        if action['jetton']['address'] != Address(Config.app_settings['jetton_master_address']).to_str(is_user_friendly=False):
                            continue
                        if action['jetton']['symbol'] != Config.app_settings['token_symbol']:
                            continue

                        transaction_amount = float(action["amount"])/(10**action['jetton']['decimals'])
                        if amount == transaction_amount:
                            transaction_id = transaction['event_id']
                            break
            
            if transaction_id:
                break

    if transaction_id is None:
        await inc_balance(db, destination_address, amount)
        raise Exception(f'Не получилось перевести пользователю {destination_address} {amount} валюты')

    await create_transaction_history(
        db, transaction_id, Address(Config.app_settings['our_wallet']).to_str(is_user_friendly=False), destination_address, "withdraw", amount
    )
