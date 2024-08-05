from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.common.admin import check_admin_token
from app.database.mongo import get_db
from app.models.event.event_model import EventBase
from app.database.event import create_event, get_upcoming_event


router = APIRouter(
    dependencies=[Depends(check_admin_token)]
)


@router.post('/create', summary='Create new event', status_code=201, responses={400: {}})
async def create(event_data: EventBase, db: AsyncIOMotorDatabase = Depends(get_db)):
    await create_event(db, **event_data)


@router.get('/upcoming', summary='Get upcoming event', response_model=EventBase, responses={400: {}})
async def upcoming(db: AsyncIOMotorDatabase = Depends(get_db)):
    return await get_upcoming_event(db)