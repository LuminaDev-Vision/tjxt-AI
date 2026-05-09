from app.agents.base import AbstractAgent
from app.core.prompts import PromptKey
from app.schemas.enums import AgentTypeEnum


class RouteAgent(AbstractAgent):

    def get_agent_type(self) -> AgentTypeEnum:
        return AgentTypeEnum.ROUTE

    @property
    def prompt_key(self) -> PromptKey:
        return PromptKey.ROUTE_AGENT
