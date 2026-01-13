from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from app.db import SessionLocal
from app.security import decode_token
from app.models import User

oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_db():
    async with SessionLocal() as session:
        yield session

async def get_current_user(token: str = Depends(oauth2), db: AsyncSession = Depends(get_db)) -> User:
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(401, "Invalid token")
        user_id = int(sub)
    except (JWTError, ValueError):
        raise HTTPException(401, "Invalid token")

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(401, "User not found")
    if user.is_blocked:
        raise HTTPException(403, "User is blocked")
    return user
