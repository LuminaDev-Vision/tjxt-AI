from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import CurrentUserId
from app.schemas.chat import ChatDTO, TemplateVO

router = APIRouter()

_TEMPLATE_VO = TemplateVO()


@router.get("/templates")
async def get_templates() -> TemplateVO:
    return _TEMPLATE_VO


@router.post("")
async def chat(
    dto: ChatDTO,
    user_id: CurrentUserId,
):
    from app.services.chat_service import ChatService

    svc = ChatService()

    async def event_generator():
        async for event in svc.chat(dto.question, dto.session_id, user_id):
            yield f"data: {event.model_dump_json()}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/stop")
async def stop(session_id: str):
    from app.services.chat_service import ChatService

    svc = ChatService()
    svc.stop(session_id)


@router.post("/text")
async def chat_text(question: str) -> str:
    from app.services.chat_service import ChatService

    svc = ChatService()
    return await svc.chat_text(question)
