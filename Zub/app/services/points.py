from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, ScoreEvent, AppSetting, DAILY_POINTS_LIMIT_KEY

def _start_of_day(dt: datetime) -> datetime:
    return datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc)

def _start_of_week(dt: datetime) -> datetime:
    start_day = dt - timedelta(days=dt.weekday())
    return datetime(start_day.year, start_day.month, start_day.day, tzinfo=timezone.utc)

async def get_daily_limit(session: AsyncSession) -> int:
    row = await session.get(AppSetting, DAILY_POINTS_LIMIT_KEY)
    if not row:
        return 0
    return int(row.value.get("limit", 0))

async def ensure_resets(user: User) -> None:
    now = datetime.now(timezone.utc)
    sod = _start_of_day(now)
    sow = _start_of_week(now)

    if not user.last_daily_reset_at or user.last_daily_reset_at < sod:
        user.daily_points = 0
        user.last_daily_reset_at = now

    if not user.last_weekly_reset_at or user.last_weekly_reset_at < sow:
        user.weekly_points = 0
        user.last_weekly_reset_at = now

async def add_points(session: AsyncSession, user: User, amount: int, reason: str | None):
    await ensure_resets(user)
    daily_limit = await get_daily_limit(session)

    if daily_limit > 0:
        remaining = max(0, daily_limit - user.daily_points)
        accepted = min(amount, remaining)
    else:
        accepted = amount
        remaining = -1

    if accepted <= 0:
        return 0, (0 if daily_limit > 0 else -1)

    user.total_points += accepted
    user.daily_points += accepted
    user.weekly_points += accepted

    session.add(ScoreEvent(user_id=user.id, amount=accepted, reason=reason))
    return accepted, (max(0, daily_limit - user.daily_points) if daily_limit > 0 else -1)
