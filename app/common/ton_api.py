import aiohttp

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