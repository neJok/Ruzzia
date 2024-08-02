from motor.motor_asyncio import AsyncIOMotorDatabase

from datetime import time

from app.models.event.event_model import EventResponse
from app.common.time import convert_to_iso8601
from app.config import Config


__db_collection = 'events'

async def create_event(
        conn: AsyncIOMotorDatabase,
        name: str,
        start_time: time
) -> None:
    expire_at = convert_to_iso8601(start_time, Config.app_settings.get('default_timezone'))
    await conn[__db_collection].insert_one({
        "name": name,
        "start_time": start_time,
        "expire_at": expire_at
    })


async def get_upcoming_event(conn: AsyncIOMotorDatabase) -> EventResponse:
    events = await conn[__db_collection].find({}, {"_id": 0, "expired_at": 0}).sort("start_time", 1).to_list(length=1)
    upcoming_event = events[0]
    return EventResponse(**upcoming_event)
