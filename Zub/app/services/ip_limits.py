from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import IP_DAILY_LIMIT_KEY
from app.services.settings import get_setting_int
from app.services.redis_cache import get_redis, ttl_until_day_end

async def check_ip_limit(session: AsyncSession, ip_address: str | None) -> tuple[bool, int]:
    if not ip_address:
        return True, -1
    limit = await get_setting_int(session, IP_DAILY_LIMIT_KEY, default=0)
    if limit <= 0:
        return True, -1
    redis = get_redis()
    if not redis:
        return True, -1
    day_key = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    key = f"ip_limit:{day_key}:{ip_address}"
    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, ttl_until_day_end())
    remaining = max(0, limit - current)
    return current <= limit, remaining
