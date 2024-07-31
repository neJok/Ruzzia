from fastapi import APIRouter, Depends, Response

from app.database.mongo import get_db, AsyncIOMotorClient
from app.database.user import get_user_by_address
from app.models.user.get_user import GetUserResp

router = APIRouter()


@router.get('/', include_in_schema=False, status_code=200)
@router.get('', response_model=GetUserResp, status_code=200,
            responses={
                400: {}
            }
            )
async def get_user(
    addresss: str,
    db: AsyncIOMotorClient = Depends(get_db),
):

    user = await get_user_by_address(
        db,
        addresss
    )

    if user is None:
        return Response(status_code=204)

    return GetUserResp(name=user.get("name"))
