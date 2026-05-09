from app.agents.base import AbstractAgent
from app.core.prompts import PromptKey
from app.schemas.enums import AgentTypeEnum
from app.tools.order_tools import ORDER_TOOLS


class BuyAgent(AbstractAgent):

    def get_agent_type(self) -> AgentTypeEnum:
        return AgentTypeEnum.BUY

    @property
    def prompt_key(self) -> PromptKey:
        return PromptKey.BUY_AGENT

    def tools(self) -> list[dict]:
        return ORDER_TOOLS
