import logging
from datetime import datetime

import redis.asyncio as redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.memory.message_util import to_dashscope_messages
from app.memory.redis_chat_memory import RedisChatMemory
from app.models.chat_session import ChatSession
from app.schemas.session import ChatSessionVO, MessageVO, SessionHistoryVO, SessionVO
from app.utils.common import generate_session_id, group_sessions_by_time

logger = logging.getLogger(__name__)


class SessionService:

    def __init__(self, db: AsyncSession | None, redis_client: redis.Redis):
        self.db = db
        self.memory = RedisChatMemory(redis_client)

    async def create_session(self, user_id: int) -> SessionVO:
        session_id = generate_session_id()
        session_obj = ChatSession(
            session_id=session_id,
            user_id=user_id,
            title=settings.SESSION_TITLE,
            creater=user_id,
            updater=user_id,
        )
        if self.db:
            self.db.add(session_obj)
            await self.db.commit()

        return SessionVO(
            session_id=session_id,
            title=settings.SESSION_TITLE,
            describe=settings.SESSION_DESCRIBE,
            examples=[],
        )

    async def get_messages(self, user_id: int, session_id: str) -> list[MessageVO]:
        conversation_id = f"{user_id}_{session_id}"
        history = await self.memory.get(conversation_id)
        messages = []
        for msg in history:
            msg_type = msg.get("messageType", "")
            if msg_type == "USER":
                messages.append(MessageVO(type=1, content=msg.get("textContent")))
            elif msg_type == "ASSISTANT":
                messages.append(
                    MessageVO(type=2, content=msg.get("textContent"), params=msg.get("params"))
                )
        return messages

    async def get_history(self, user_id: int) -> list[SessionHistoryVO]:
        if not self.db:
            return []
        stmt = (
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.update_time.desc())
        )
        result = await self.db.execute(stmt)
        sessions = result.scalars().all()

        session_vos = [
            ChatSessionVO(
                session_id=s.session_id,
                title=s.title,
                update_time=s.update_time,
            )
            for s in sessions
        ]
        grouped = group_sessions_by_time([sv.model_dump() for sv in session_vos])
        return [SessionHistoryVO(**g) for g in grouped]

    async def delete_session(self, user_id: int, session_id: str):
        conversation_id = f"{user_id}_{session_id}"
        await self.memory.clear(conversation_id)
        if self.db:
            stmt = select(ChatSession).where(
                ChatSession.user_id == user_id,
                ChatSession.session_id == session_id,
            )
            result = await self.db.execute(stmt)
            session_obj = result.scalar_one_or_none()
            if session_obj:
                await self.db.delete(session_obj)
                await self.db.commit()

    async def update_title(self, user_id: int, session_id: str, title: str):
        if self.db:
            stmt = select(ChatSession).where(
                ChatSession.user_id == user_id,
                ChatSession.session_id == session_id,
            )
            result = await self.db.execute(stmt)
            session_obj = result.scalar_one_or_none()
            if session_obj:
                session_obj.title = title[:100]
                session_obj.update_time = datetime.now()
                await self.db.commit()

    @staticmethod
    def get_hot_questions() -> list[str]:
        return [
            "推荐一些热门课程",
            "如何购买课程？",
            "课程有什么优惠活动？",
            "如何查看学习进度？",
        ]
