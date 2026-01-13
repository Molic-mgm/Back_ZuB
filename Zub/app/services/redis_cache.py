import json
from datetime import datetime, timezone
from redis.asyncio import from_url, Redis

from app.config import settings

_redis: Redis | None = None

def get_redis() -> Redis | None:
    global _redis
    if not settings.REDIS_URL:
        return None
    if _redis is None:
        _redis = from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    return _redis

def leaderboard_cache_key() -> str:
    return "leaderboard:top10"

async def get_cached_leaderboard() -> list[dict] | None:
    redis = get_redis()
    if not redis or settings.LEADERBOARD_CACHE_TTL_SEC <= 0:
        return None
    cached = await redis.get(leaderboard_cache_key())
    if not cached:
        return None
    return json.loads(cached)

async def set_cached_leaderboard(entries: list[dict]) -> None:
    redis = get_redis()
    if not redis or settings.LEADERBOARD_CACHE_TTL_SEC <= 0:
        return
    await redis.setex(
        leaderboard_cache_key(),
        settings.LEADERBOARD_CACHE_TTL_SEC,
        json.dumps(entries, ensure_ascii=False),
    )

async def invalidate_leaderboard_cache() -> None:
    redis = get_redis()
    if not redis:
        return
    await redis.delete(leaderboard_cache_key())

def ttl_until_day_end() -> int:
    now = datetime.now(timezone.utc)
    end = datetime(now.year, now.month, now.day, tzinfo=timezone.utc).replace(hour=23, minute=59, second=59)
    return max(60, int((end - now).total_seconds()))
