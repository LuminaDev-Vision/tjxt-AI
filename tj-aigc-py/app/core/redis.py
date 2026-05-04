import redis.asyncio as redis

from app.core.config import settings

_redis: redis.Redis | None = None


async def init_redis():
    global _redis
    _redis = redis.from_url(settings.REDIS_URL, decode_responses=True)


async def close_redis():
    global _redis
    if _redis:
        await _redis.close()
        _redis = None


def get_redis() -> redis.Redis:
    if _redis is None:
        raise RuntimeError("Redis not initialized")
    return _redis
