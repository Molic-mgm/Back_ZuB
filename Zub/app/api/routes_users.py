from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.schemas import UserOut
from app.models import User
from app.services.points import ensure_resets

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await ensure_resets(user)
    await db.commit()
    await db.refresh(user)
    return UserOut.model_validate(user, from_attributes=True)
