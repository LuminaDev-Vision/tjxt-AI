import logging
from collections.abc import AsyncGenerator

from app.agents.registry import get_agent
from app.agents.route_agent import RouteAgent
from app.clients.openai_client import openai_chat_text
from app.core.prompts import PromptKey, prompt_manager
from app.memory.redis_chat_memory import RedisChatMemory
from app.schemas.chat import ChatEventVO, STOP_EVENT
from app.schemas.enums import AgentTypeEnum, ChatEventTypeEnum

logger = logging.getLogger(__name__)


class ChatService:

    def __init__(self):
        self.memory = RedisChatMemory()
        self._route_agent = RouteAgent()

    async def chat(
        self, question: str, session_id: str, user_id: int
    ) -> AsyncGenerator[ChatEventVO, None]:
        # Step 1: RouteAgent 非流式分类
        route_result = await self._route_agent.process(question, session_id, user_id)
        logger.info("Route result: %s", route_result)

        agent_type = AgentTypeEnum.from_name(route_result)
        if agent_type is None:
            yield ChatEventVO(eventData=route_result, eventType=ChatEventTypeEnum.DATA)
            yield STOP_EVENT
            return

        agent = get_agent(agent_type)
        if agent is None:
            yield ChatEventVO(eventData=route_result, eventType=ChatEventTypeEnum.DATA)
            yield STOP_EVENT
            return

        # Step 2: 清除路由中间记录
        conversation_id = f"{user_id}_{session_id}"
        await self.memory.optimization(conversation_id)

        # Step 3: 具体 Agent 流式执行
        async for event in agent.process_stream(question, session_id, user_id):
            yield event

    def stop(self, session_id: str):
        self._route_agent.stop(session_id)
        from app.agents.registry import get_all_agents

        for a in get_all_agents().values():
            a.stop(session_id)

    async def chat_text(self, question: str) -> str:
        messages = [
            {"role": "system", "content": prompt_manager.get(PromptKey.TEXT)},
            {"role": "user", "content": question},
        ]
        return await openai_chat_text(messages)
