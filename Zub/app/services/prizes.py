from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Prize, UserPrize, User

async def list_active_prizes(session: AsyncSession) -> list[Prize]:
    q = select(Prize).where(Prize.is_active == True).order_by(Prize.place_from)  # noqa
    res = await session.execute(q)
    return res.scalars().all()

def find_prize_for_place(prizes: list[Prize], place: int) -> Prize | None:
    for prize in prizes:
        if prize.place_from <= place <= prize.place_to:
            return prize
    return None

async def assign_prize(session: AsyncSession, user: User, prize: Prize, issued_by: str | None, notes: str | None) -> UserPrize:
    user_prize = UserPrize(user_id=user.id, prize_id=prize.id, issued_by=issued_by, notes=notes)
    session.add(user_prize)
    await session.flush()
    return user_prize

def start_of_day_utc() -> datetime:
    now = datetime.now(timezone.utc)
    return datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

async def assignment_exists_today(session: AsyncSession, user_id: int, prize_id: int) -> bool:
    since = start_of_day_utc()
    q = select(UserPrize).where(
        UserPrize.user_id == user_id,
        UserPrize.prize_id == prize_id,
        UserPrize.awarded_at >= since,
    )
    res = await session.execute(q)
    return res.scalar_one_or_none() is not None
