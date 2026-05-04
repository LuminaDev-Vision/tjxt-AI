from fastapi import APIRouter

from app.api.routes import audio, chat, embedding, session

api_router = APIRouter()
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(session.router, prefix="/session", tags=["session"])
api_router.include_router(audio.router, prefix="/audio", tags=["audio"])
api_router.include_router(embedding.router, prefix="/embedding", tags=["embedding"])
