import aiohttp

from app.config import Config


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
        

async def get_account_info(address: str):
    """Get basic information about the address: balance, code, data, last_transaction_id."""

    url = f"https://toncenter.com/api/v2/getAddressInformation?address={address}"
    headers = {
        'accept': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            account_info = await response.json()
            return account_info
        
async def get_last_transactions(wallet: str):
    """Get last address transactions"""

    url = f"https://tonapi.io/v2/accounts/{wallet}/jettons/{Config.app_settings['jetton_master_address']}/history?limit=100"
    headers = {
        'accept': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return data
        

