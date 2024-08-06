import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    version = "0.1.0"
    title = "ruzzia"

    app_settings = {
        'db_name': os.getenv('MONGO_DB'),
        'mongodb_url': os.getenv('MONGO_URL'),
        'db_username': os.getenv('MONGO_USER'),
        'db_password': os.getenv('MONGO_PASSWORD'),

        'ton_connect_secret': os.getenv('TON_CONNECT_SECRET'),
        'payload_ttl': int(os.getenv('PAYLOAD_TTL')),
        'proof_ttl': int(os.getenv('PROOF_TTL')),
        'our_wallet': os.getenv('OUR_WALLET'),
        'jetton_master_address': os.getenv('JETTON_MASTER_ADDRESS'),
        'token_symbol': os.getenv('TOKEN_SYMBOL'),

        'access_secret_key': os.getenv('JWT_ACCESS_SECRET_KEY'),
        'access_token_expire_minutes': int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES')),
        'refresh_secret_key': os.getenv('JWT_REFRESH_SECRET_KEY'),
        'refresh_token_expire_minutes': int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_MINUTES')),

        'discord_client_id': os.getenv('DISCORD_CLIENT_ID'),
        'discord_client_secret': os.getenv('DISCORD_CLIENT_SECRET'),
        'discord_redirect_uri': os.getenv('DISCORD_REDIRECT_URI'),
        'discord_bot_token': os.getenv('DISCORD_BOT_TOKEN'),
        'discord_guild_id': os.getenv('DISCORD_GUILD_ID'),
        'discord_logs_channel_id': os.getenv('DISCORD_LOGS_CHANNEL_ID'),

        'frontend_uri': os.getenv('FRONTEND_URI'),
        
        'admin_secret_key': os.getenv('ADMIN_SECRET_KEY'),

        'default_timezone': os.getenv('DEFAULT_TIMEZONE'),
    }

    privilege_mapper = {
        0: "tourist",
        100: "worker",
        500: "citizen",
        1000: "aristocrat",
        5000: "apostle"
    }

    privilege_roles = {
        "tourist": "1268593987254485053",
        "worker": "1268594072994447440",
        "citizen": "1268594127809937461",
        "aristocrat": "1268594162530516992",
        "apostle": "1268594193618436248"
    }
