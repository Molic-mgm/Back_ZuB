from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models import User
from app.schemas import ReferralUpdateIn, ReferralOut

router = APIRouter(prefix="/referrals", tags=["referrals"])

@router.post("/update", response_model=ReferralOut)
async def update_referrals(
    body: ReferralUpdateIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user.referral_count += body.amount
    await db.commit()
    await db.refresh(user)
    return ReferralOut(referral_count=user.referral_count)
