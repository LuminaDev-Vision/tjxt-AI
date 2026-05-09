from datetime import datetime
from typing import Any

from app.agents.base import AbstractAgent
from app.core.prompts import PromptKey
from app.schemas.enums import AgentTypeEnum
from app.tools.course_tools import COURSE_TOOLS


class ConsultAgent(AbstractAgent):

    def get_agent_type(self) -> AgentTypeEnum:
        return AgentTypeEnum.CONSULT

    @property
    def prompt_key(self) -> PromptKey:
        return PromptKey.CONSULT_AGENT

    def system_message_params(self) -> dict[str, Any]:
        return {"now": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    def tools(self) -> list[dict]:
        return COURSE_TOOLS

    def advisors(self) -> dict[str, Any]:
        return {"vector_search_top_k": 999}
