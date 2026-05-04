from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    from app.core.redis import init_redis, close_redis
    from app.core.database import init_db
    from app.clients.vector_client import init_vector_db, close_vector_db
    from app.agents.registry import init_agents

    await init_redis()
    await init_db()
    await init_vector_db()
    init_agents()
    yield
    # shutdown
    await close_vector_db()
    await close_redis()


app = FastAPI(
    title=settings.APP_NAME,
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
