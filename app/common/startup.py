import asyncio

from app.database.mongo import connect_and_init_db, get_db
from app.redis.redis import connect_and_init_redis
from app.common.ton_api import get_last_transactions

async def check_trasactions_task():
    db = await get_db()

    while True:
        # await get_last_transactions(db)
        await asyncio.sleep(10)

async def startup():
    await connect_and_init_db()
    await connect_and_init_redis()
    asyncio.create_task(check_trasactions_task())
