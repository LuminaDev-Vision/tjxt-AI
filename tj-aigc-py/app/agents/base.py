import logging
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any

from app.memory.redis_chat_memory import RedisChatMemory
from app.schemas.chat import ChatEventVO, STOP_EVENT
from app.schemas.enums import AgentTypeEnum, ChatEventTypeEnum
from app.utils.common import generate_request_id

logger = logging.getLogger(__name__)


class AbstractAgent(ABC):
    _generate_status: dict[str, bool] = {}

    def __init__(self):
        self.memory = RedisChatMemory()

    @abstractmethod
    def get_agent_type(self) -> AgentTypeEnum: ...

    @abstractmethod
    def system_message(self) -> str: ...

    def system_message_params(self) -> dict[str, Any]:
        return {}

    def tools(self) -> list[dict]:
        return []

    def tool_context(self, session_id: str, request_id: str, user_id: int) -> dict:
        return {}

    def advisors(self) -> dict[str, Any]:
        return {}

    def stop(self, session_id: str):
        self._generate_status.pop(session_id, None)

    async def process(self, question: str, session_id: str, user_id: int) -> str:
        from app.clients.dashscope_client import dashscope_chat

        messages = [
            {"role": "system", "content": self.system_message()},
            {"role": "user", "content": question},
        ]
        return await dashscope_chat(messages)

    async def process_stream(
        self, question: str, session_id: str, user_id: int
    ) -> AsyncGenerator[ChatEventVO, None]:
        from app.clients.dashscope_client import dashscope_chat_stream
        from app.tools.base import ToolResultHolder

        request_id = generate_request_id()
        conversation_id = f"{user_id}_{session_id}"
        self._generate_status[session_id] = True

        # load history
        history = await self.memory.get(conversation_id)
        from app.memory.message_util import to_dashscope_messages

        messages = to_dashscope_messages(history)
        messages.insert(0, {"role": "system", "content": self.system_message()})
        messages.append({"role": "user", "content": question})

        # save user message
        from app.memory.message_util import to_user_message

        await self.memory.add(conversation_id, to_user_message(question))

        tools = self.tools()
        full_response = ""

        try:
            async for text in dashscope_chat_stream(messages, tools if tools else None):
                if not self._generate_status.get(session_id):
                    break
                full_response += text
                yield ChatEventVO(eventData=text, eventType=ChatEventTypeEnum.DATA)
        except Exception as e:
            logger.error("Agent stream error: %s", e)
        finally:
            self._generate_status.pop(session_id, None)

        # tool result param event
        tool_result = ToolResultHolder.get(request_id)
        if tool_result:
            yield ChatEventVO(eventData=tool_result, eventType=ChatEventTypeEnum.PARAM)
            ToolResultHolder.remove(request_id)

        # save assistant message
        from app.memory.message_util import to_assistant_message

        await self.memory.add(conversation_id, to_assistant_message(full_response))

        yield STOP_EVENT
