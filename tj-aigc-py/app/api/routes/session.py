from fastapi import APIRouter

from app.api.deps import CurrentUserId, RedisDep, SessionDep
from app.schemas.session import SessionVO

router = APIRouter()


@router.post("")
async def create_session(
    user_id: CurrentUserId,
    session: SessionDep,
    redis_client: RedisDep,
) -> SessionVO:
    from app.services.session_service import SessionService

    svc = SessionService(session, redis_client)
    return await svc.create_session(user_id)


@router.get("/hot")
async def get_hot_questions() -> list[str]:
    from app.services.session_service import SessionService

    return SessionService.get_hot_questions()


@router.get("/{session_id}")
async def get_session_messages(
    session_id: str,
    user_id: CurrentUserId,
    redis_client: RedisDep,
):
    from app.services.session_service import SessionService

    svc = SessionService(None, redis_client)
    return await svc.get_messages(user_id, session_id)


@router.get("/history")
async def get_session_history(
    user_id: CurrentUserId,
    session: SessionDep,
    redis_client: RedisDep,
):
    from app.services.session_service import SessionService

    svc = SessionService(session, redis_client)
    return await svc.get_history(user_id)


@router.delete("/history")
async def delete_session(
    session_id: str,
    user_id: CurrentUserId,
    session: SessionDep,
    redis_client: RedisDep,
):
    from app.services.session_service import SessionService

    svc = SessionService(session, redis_client)
    await svc.delete_session(user_id, session_id)


@router.put("/history")
async def update_session_title(
    session_id: str,
    title: str,
    user_id: CurrentUserId,
    session: SessionDep,
    redis_client: RedisDep,
):
    from app.services.session_service import SessionService

    svc = SessionService(session, redis_client)
    await svc.update_title(user_id, session_id, title)
