from app.agents.base import AbstractAgent
from app.core.prompts import get_prompt
from app.schemas.enums import AgentTypeEnum


class KnowledgeAgent(AbstractAgent):

    def get_agent_type(self) -> AgentTypeEnum:
        return AgentTypeEnum.KNOWLEDGE

    def system_message(self) -> str:
        return get_prompt("knowledge_agent")
