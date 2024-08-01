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

        'access_secret_key': os.getenv('JWT_ACCESS_SECRET_KEY'),
        'access_token_expire_minutes': int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES')),
        'refresh_secret_key': os.getenv('JWT_REFRESH_SECRET_KEY'),
        'refresh_token_expire_minutes': int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_MINUTES')),

        'discord_client_id': os.getenv('DISCORD_CLIENT_ID'),
        'discord_client_secret': os.getenv('DISCORD_CLIENT_SECRET'),
        'discord_redirect_uri': os.getenv('DISCORD_REDIRECT_URI'),

        'frontend_uri': os.getenv('FRONTEND_URI')
    }
