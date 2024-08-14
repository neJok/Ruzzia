from pytoniq import LiteBalancer, WalletV4R2, begin_cell
from pytoniq_core import Address
from motor.motor_asyncio import AsyncIOMotorDatabase

import asyncio

from app.config import Config
from app.database.transaction_history import create_transaction_history
from app.common.ton_api import get_account_info

async def send_tokens_to_address(db: AsyncIOMotorDatabase, destination_address: str, amount: float):
    provider = LiteBalancer.from_mainnet_config(1)
    await provider.start_up()

    wallet = await WalletV4R2.from_mnemonic(provider=provider, mnemonics=mnemonics)
    USER_ADDRESS = wallet.address

    USER_JETTON_WALLET = (await provider.run_get_method(address=Address(Config.app_settings['jetton_master_address']).to_str(is_user_friendly=True, is_bounceable=True, is_url_safe=True),
                                                        method="get_wallet_address",
                                                        stack=[begin_cell().store_address(USER_ADDRESS).end_cell().begin_parse()]))[0].load_address()
    
    DESTINATION_ADDRESS = Address(destination_address).to_str(is_user_friendly=True, is_bounceable=True, is_url_safe=True)
    forward_payload = (begin_cell()
                      .store_uint(0, 32)
                      .store_snake_string("Conclusion | ruzzia.org")
                      .end_cell())
    transfer_cell = (begin_cell()
                    .store_uint(0xf8a7ea5, 32)
                    .store_uint(0, 64)
                    .store_coins(int(amount * 10**9))
                    .store_address(DESTINATION_ADDRESS) # Destination address
                    .store_address(USER_ADDRESS)
                    .store_bit(0)
                    .store_coins(1)
                    .store_bit(1)
                    .store_ref(forward_payload)
                    .end_cell())

    account_info = await get_account_info(USER_JETTON_WALLET)
    last_transaction_id = account_info["result"]["last_transaction_id"]["hash"]

    await wallet.transfer(destination=USER_JETTON_WALLET, amount=int(0.05 * 1e9), body=transfer_cell)

    transaction_id = last_transaction_id
    while transaction_id == last_transaction_id:
        await asyncio.sleep(1500)
        account_info = await get_account_info(USER_JETTON_WALLET)
        transaction_id = account_info["result"]["last_transaction_id"]["hash"]

    await create_transaction_history(
        db, transaction_id, USER_JETTON_WALLET, DESTINATION_ADDRESS, "withdraw", amount
    )
    await provider.close_all()
