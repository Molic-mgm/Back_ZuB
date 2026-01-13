from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.schemas import PointsAddIn, UserOut
from app.models import User
from app.services.points import add_points

router = APIRouter(prefix="/points", tags=["points"])

@router.post("/add", response_model=UserOut)
async def add(body: PointsAddIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    accepted, _remaining = await add_points(db, user, body.amount, body.reason)
    if accepted <= 0:
        raise HTTPException(429, "Daily limit reached")

    await db.commit()
    await db.refresh(user)
    return UserOut.model_validate(user, from_attributes=True)
