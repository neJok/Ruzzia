from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase


from app.common.error import UnauthorizatedError
from app.config import Config
from app.database.mongo import get_db 

security = HTTPBearer()

async def check_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncIOMotorDatabase = Depends(get_db)) -> bool:
    credentials_exception = UnauthorizatedError(["Could not validate credentials"])
    token = credentials.credentials
    
    if token != Config.app_settings['admin_secret_key']:
        raise credentials_exception
    
    return True