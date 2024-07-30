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
    }
