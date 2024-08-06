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
        

async def add_role_to_user(user_id, role_id):
    url = f"https://discord.com/api/v9/guilds/{Config.app_settings['discord_guild_id']}/members/{user_id}/roles/{role_id}"
    headers = {
        "Authorization": f"Bot {Config.app_settings['discord_bot_token']}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.put(url, headers=headers) as response:
            if response.status == 204:
                print(f"Role {role_id} successfully added to user {user_id}")
            else:
                print(f"Failed to add role: {response.status}")
                print(await response.text())


async def remove_role_from_user(user_id, role_id):
    url = f"https://discord.com/api/v9/guilds/{Config.app_settings['discord_guild_id']}/members/{user_id}/roles/{role_id}"
    headers = {
        "Authorization": f"Bot {Config.app_settings['discord_bot_token']}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.delete(url, headers=headers) as response:
            if response.status == 204:
                print(f"Role {role_id} successfully removed from user {user_id}")
            else:
                print(f"Failed to remove role: {response.status}")
                print(await response.text())


async def send_message_to_logs(message):
    url = f"https://discord.com/api/v9/channels/{Config.app_settings['disord_logs_channel_iddisord_logs_channel_id']}/messages"
    headers = {
        "Authorization": f"Bot {Config.app_settings['discord_bot_token']}",
        "Content-Type": "application/json"
    }
    json_data = {
        "content": message
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=json_data) as response:
            if response.status == 200 or response.status == 201:
                print(f"Message successfully sent to channel")
            else:
                print(f"Failed to send message: {response.status}")
                print(await response.text())