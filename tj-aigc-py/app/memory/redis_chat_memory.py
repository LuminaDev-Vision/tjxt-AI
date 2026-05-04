import json
from typing import Any

import redis.asyncio as redis

from app.core.redis import get_redis

KEY_PREFIX = "chat:"


class RedisChatMemory:

    def __init__(self, redis_client: redis.Redis | None = None):
        self._redis = redis_client

    @property
    def r(self) -> redis.Redis:
        return self._redis or get_redis()

    def _key(self, conversation_id: str) -> str:
        return f"{KEY_PREFIX}{conversation_id}"

    async def add(self, conversation_id: str, message: dict[str, Any]):
        await self.r.rpush(self._key(conversation_id), json.dumps(message, ensure_ascii=False))

    async def get(self, conversation_id: str, last_n: int = 100) -> list[dict]:
        data = await self.r.lrange(self._key(conversation_id), 0, last_n - 1)
        return [json.loads(item) for item in data]

    async def clear(self, conversation_id: str):
        await self.r.delete(self._key(conversation_id))

    async def optimization(self, conversation_id: str):
        key = self._key(conversation_id)
        length = await self.r.llen(key)
        if length >= 2:
            await self.r.rpop(key)
            await self.r.rpop(key)
