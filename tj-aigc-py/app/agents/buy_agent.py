from app.agents.base import AbstractAgent
from app.core.prompts import get_prompt
from app.schemas.enums import AgentTypeEnum
from app.tools.order_tools import ORDER_TOOLS


class BuyAgent(AbstractAgent):

    def get_agent_type(self) -> AgentTypeEnum:
        return AgentTypeEnum.BUY

    def system_message(self) -> str:
        return get_prompt("buy_agent")

    def tools(self) -> list[dict]:
        return ORDER_TOOLS
