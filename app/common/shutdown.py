from app.database.mongo import close_db_connect
from app.redis.redis import close_redis_connect


async def shutdown():
    await close_db_connect()
    await close_redis_connect()
    