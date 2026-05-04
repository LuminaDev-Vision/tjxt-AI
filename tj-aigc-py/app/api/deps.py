from typing import Annotated

import redis.asyncio as redis
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import get_redis

SessionDep = Annotated[AsyncSession, Depends(get_db)]
RedisDep = Annotated[redis.Redis, Depends(get_redis)]


def get_current_user_id(request: Request) -> int:
    return int(request.headers.get("X-User-Id", 0))


CurrentUserId = Annotated[int, Depends(get_current_user_id)]
