from app.agents.base import AbstractAgent
from app.core.prompts import PromptKey
from app.schemas.enums import AgentTypeEnum


class KnowledgeAgent(AbstractAgent):

    def get_agent_type(self) -> AgentTypeEnum:
        return AgentTypeEnum.KNOWLEDGE

    @property
    def prompt_key(self) -> PromptKey:
        return PromptKey.KNOWLEDGE_AGENT
