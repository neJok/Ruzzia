from dotenv import load_dotenv
from redis.asyncio import Redis

import logging

from app.config import Config

load_dotenv()

redis_client: Redis | None = None


async def get_redis() -> Redis:
    return redis_client


async def connect_and_init_redis():
    global redis_client
    try:
        redis_client = Redis(
            host=Config.app_settings.get('redis_host'),
            port=int(Config.app_settings.get('redis_port')),
            password=Config.app_settings.get('redis_password'),
        )
        logging.info(f"Successfull ping: {await redis_client.ping()}")
        logging.info('Connected to redis.')
    except Exception as e:
        logging.exception(f'Could not connect to redis: {e}')
        raise


async def close_redis_connect():
    global redis_client
    if redis_client is None:
        return
    
    redis_client.close()
    redis_client = None