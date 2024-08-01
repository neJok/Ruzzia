import aiohttp
from app.config import Config

async def authorize_discord(code: str)-> str:
    """Authorize and get discord access token"""

    url = 'https://discord.com/api/oauth2/token'
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "client_id": int(Config.app_settings['discord_client_id']),
        "client_secret": Config.app_settings['discord_client_secret'],
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": Config.app_settings['discord_redirect_uri'],
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as response:
            result = await response.json()
            return result['access_token']
        

async def get_user_discord_id(access_token: str)-> int:
    """Authorize and get discord access token"""

    url = 'https://discord.com/api/users/@me'
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            result = await response.json()
            return int(result['id'])