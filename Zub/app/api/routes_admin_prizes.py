from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.config import settings
from app.models import Prize, User
from app.schemas import (
    PrizeCreateIn,
    PrizeAssignIn,
    PrizeAssignOut,
    PrizeOut,
    PrizeAssignBatchOut,
    PrizeAssignSkipped,
)
from app.services.prizes import assign_prize, assignment_exists_today, list_active_prizes, find_prize_for_place
from app.services.leaderboard import get_top10_users

router = APIRouter(prefix="/admin/prizes", tags=["admin"])

def _basic_admin_guard(x_admin_user: str | None, x_admin_pass: str | None):
    if x_admin_user != settings.ADMIN_USERNAME or x_admin_pass != settings.ADMIN_PASSWORD:
        raise HTTPException(401, "Admin auth failed")

@router.get("", response_model=list[PrizeOut])
async def list_prizes(
    db: AsyncSession = Depends(get_db),
    x_admin_user: str | None = Header(default=None),
    x_admin_pass: str | None = Header(default=None),
):
    _basic_admin_guard(x_admin_user, x_admin_pass)
    res = await db.execute(select(Prize).order_by(Prize.place_from))
    prizes = res.scalars().all()
    return [
        PrizeOut(
            title=prize.title,
            description=prize.description,
            place_from=prize.place_from,
            place_to=prize.place_to,
            is_active=prize.is_active,
        )
        for prize in prizes
    ]

@router.post("", response_model=PrizeOut)
async def create_prize(
    body: PrizeCreateIn,
    db: AsyncSession = Depends(get_db),
    x_admin_user: str | None = Header(default=None),
    x_admin_pass: str | None = Header(default=None),
):
    _basic_admin_guard(x_admin_user, x_admin_pass)
    prize = Prize(
        title=body.title,
        description=body.description,
        place_from=body.place_from,
        place_to=body.place_to,
        is_active=body.is_active,
    )
    db.add(prize)
    await db.commit()
    await db.refresh(prize)
    return PrizeOut(
        title=prize.title,
        description=prize.description,
        place_from=prize.place_from,
        place_to=prize.place_to,
        is_active=prize.is_active,
    )

@router.post("/assign", response_model=PrizeAssignOut)
async def assign_prize_to_user(
    body: PrizeAssignIn,
    db: AsyncSession = Depends(get_db),
    x_admin_user: str | None = Header(default=None),
    x_admin_pass: str | None = Header(default=None),
):
    _basic_admin_guard(x_admin_user, x_admin_pass)
    user = await db.get(User, body.user_id)
    if not user:
        raise HTTPException(404, "User not found")
    prize = await db.get(Prize, body.prize_id)
    if not prize:
        raise HTTPException(404, "Prize not found")

    assignment = await assign_prize(db, user, prize, issued_by=x_admin_user, notes=body.notes)
    await db.commit()
    await db.refresh(assignment)
    return PrizeAssignOut(
        user_id=assignment.user_id,
        prize_id=assignment.prize_id,
        status=assignment.status,
        issued_by=assignment.issued_by,
        notes=assignment.notes,
    )

@router.post("/assign-top10", response_model=PrizeAssignBatchOut)
async def assign_top10_prizes(
    db: AsyncSession = Depends(get_db),
    x_admin_user: str | None = Header(default=None),
    x_admin_pass: str | None = Header(default=None),
):
    _basic_admin_guard(x_admin_user, x_admin_pass)
    users = await get_top10_users(db)
    prizes = await list_active_prizes(db)
    assigned: list[PrizeAssignOut] = []
    skipped: list[PrizeAssignSkipped] = []

    for place, user in enumerate(users, start=1):
        prize = find_prize_for_place(prizes, place)
        if not prize:
            skipped.append(PrizeAssignSkipped(user_id=user.id, prize_id=0, reason="No prize for place"))
            continue
        if await assignment_exists_today(db, user.id, prize.id):
            skipped.append(PrizeAssignSkipped(user_id=user.id, prize_id=prize.id, reason="Already awarded today"))
            continue
        assignment = await assign_prize(db, user, prize, issued_by=x_admin_user, notes=f"Auto award for place {place}")
        assigned.append(
            PrizeAssignOut(
                user_id=assignment.user_id,
                prize_id=assignment.prize_id,
                status=assignment.status,
                issued_by=assignment.issued_by,
                notes=assignment.notes,
            )
        )

    await db.commit()
    return PrizeAssignBatchOut(assigned=assigned, skipped=skipped)
