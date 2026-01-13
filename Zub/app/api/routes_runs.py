from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models import User
from app.schemas import RunSubmitIn, RunSubmitOut, UserOut
from app.services.points import add_points, record_score_event, get_daily_limit, ensure_resets
from app.services.anti_cheat import is_suspicious_run
from app.services.ip_limits import check_ip_limit

router = APIRouter(prefix="/runs", tags=["runs"])

@router.post("/submit", response_model=RunSubmitOut)
async def submit_run(
    body: RunSubmitIn,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ip_address = request.client.host if request.client else None
    await ensure_resets(user)
    await db.commit()
    await db.refresh(user)

    allowed, _remaining = await check_ip_limit(db, ip_address)
    if not allowed:
        raise HTTPException(429, "IP daily limit reached")

    suspicious, _max_points = await is_suspicious_run(db, body.points)
    if suspicious:
        await record_score_event(db, user, body.points, body.reason, ip_address=ip_address, is_suspicious=True)
        await db.commit()
        await db.refresh(user)
        daily_limit = await get_daily_limit(db)
        remaining = max(0, daily_limit - user.daily_points) if daily_limit > 0 else -1
        return RunSubmitOut(
            accepted_points=0,
            rejected_points=body.points,
            daily_remaining=remaining,
            is_suspicious=True,
            user=UserOut.model_validate(user, from_attributes=True),
        )

    accepted, remaining = await add_points(db, user, body.points, body.reason, ip_address=ip_address)
    if accepted <= 0:
        raise HTTPException(429, "Daily limit reached")

    await db.commit()
    await db.refresh(user)
    return RunSubmitOut(
        accepted_points=accepted,
        rejected_points=body.points - accepted,
        daily_remaining=remaining,
        is_suspicious=False,
        user=UserOut.model_validate(user, from_attributes=True),
    )
