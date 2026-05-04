from app.agents.base import AbstractAgent
from app.core.prompts import get_prompt
from app.schemas.enums import AgentTypeEnum


class RouteAgent(AbstractAgent):

    def get_agent_type(self) -> AgentTypeEnum:
        return AgentTypeEnum.ROUTE

    def system_message(self) -> str:
        return get_prompt("route_agent")
