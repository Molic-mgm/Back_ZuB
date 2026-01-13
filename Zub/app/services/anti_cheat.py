from sqlalchemy.ext.asyncio import AsyncSession
from app.models import ANTI_CHEAT_MAX_POINTS_KEY
from app.services.settings import get_setting_int

async def is_suspicious_run(session: AsyncSession, points: int) -> tuple[bool, int]:
    max_points = await get_setting_int(session, ANTI_CHEAT_MAX_POINTS_KEY, default=0)
    if max_points > 0 and points > max_points:
        return True, max_points
    return False, max_points
