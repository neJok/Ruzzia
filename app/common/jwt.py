import jwt

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import timedelta, datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from jwt.exceptions import InvalidTokenError

from app.common.error import UauthorizatedError
from app.config import Config
from app.database.mongo import get_db
from app.database.user import get_user_by_address
from app.models.user.token import TokenData
from app.models.user.user_model import UserDB

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Config.app_settings['access_secret_key'], algorithm="HS256")
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=2)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Config.app_settings['refresh_secret_key'], algorithm="HS256")
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncIOMotorDatabase = Depends(get_db)) -> UserDB:
    token = credentials.credentials
    credentials_exception = UauthorizatedError(["Could not validate credentials"])
    try:
        payload = jwt.decode(token, Config.app_settings['access_secret_key'], algorithms=["HS256"])
        address: str | None = payload.get("sub")
        if address is None:
            raise credentials_exception
        
        token_data = TokenData(address=address)
    except InvalidTokenError:
        raise credentials_exception
    
    user = await get_user_by_address(db, token_data.address)
    if user is None:
        raise credentials_exception
    
    return user