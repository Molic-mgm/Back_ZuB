from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.services.redis_cache import get_cached_leaderboard, set_cached_leaderboard

async def get_top10_users(session: AsyncSession) -> list[User]:
    q = select(User).where(User.is_blocked == False).order_by(desc(User.total_points)).limit(10)  # noqa
    res = await session.execute(q)
    return res.scalars().all()

async def get_top10_entries(session: AsyncSession) -> list[dict]:
    cached = await get_cached_leaderboard()
    if cached is not None:
        return cached
    users = await get_top10_users(session)
    entries = [
        {"user_id": u.id, "nickname": u.nickname, "total_points": u.total_points}
        for u in users
    ]
    await set_cached_leaderboard(entries)
    return entries
