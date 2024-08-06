import aiohttp
import asyncio

async def add_role_to_user(token, guild_id, user_id, role_id):
    url = f"https://discord.com/api/v9/guilds/{guild_id}/members/{user_id}/roles/{role_id}"
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.put(url, headers=headers) as response:
            if response.status == 204:
                print(f"Role {role_id} successfully added to user {user_id}")
            else:
                print(f"Failed to add role: {response.status}")
                print(await response.text())

async def remove_role_from_user(token, guild_id, user_id, role_id):
    url = f"https://discord.com/api/v9/guilds/{guild_id}/members/{user_id}/roles/{role_id}"
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.delete(url, headers=headers) as response:
            if response.status == 204:
                print(f"Role {role_id} successfully removed from user {user_id}")
            else:
                print(f"Failed to remove role: {response.status}")
                print(await response.text())

async def send_message_to_channel(token, channel_id, message):
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json"
    }
    json_data = {
        "content": message
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=json_data) as response:
            if response.status == 200 or response.status == 201:
                print(f"Message successfully sent to channel {channel_id}")
            else:
                print(f"Failed to send message: {response.status}")
                print(await response.text())

# Пример использования
# Пример использования
token = "MTI2ODUzNzE5MTU2MzUyNjE0NQ.GBCn-R.8vg9fSg6QccIlbzwjt9gEgHdRMVWNDiyePHacw"
guild_id = "1264692366397145138"
user_id = "458666543924903936"
role_id = "1268594127809937461"
channel_id = "1269696775648706670"
message = "Hello, Discord!"

async def main():
    roles = {
        "tourist": "1268593987254485053",
        "worker": "1268594072994447440",
        "сitizen": "1268594127809937461",
        "aristocrat": "1268594162530516992",
        "apostle": "1268594193618436248"
    }
    user_old_privelegy = "apostle" # Может быть и None
    if user_old_privelegy:
        await remove_role_from_user(token, guild_id, user_id, roles[user_old_privelegy])
    old_privelegy_role = roles[user_old_privelegy]

    await add_role_to_user(token, guild_id, user_id, role_id)
    await remove_role_from_user(token, guild_id, user_id, role_id)
    await send_message_to_channel(token, channel_id, message)

asyncio.run(main())

