from typing import Any

from app.agents.base import AbstractAgent
from app.core.prompts import PromptKey
from app.schemas.enums import AgentTypeEnum
from app.tools.course_tools import COURSE_TOOLS


class RecommendAgent(AbstractAgent):

    def get_agent_type(self) -> AgentTypeEnum:
        return AgentTypeEnum.RECOMMEND

    @property
    def prompt_key(self) -> PromptKey:
        return PromptKey.RECOMMEND_AGENT

    def tools(self) -> list[dict]:
        return COURSE_TOOLS

    def advisors(self) -> dict[str, Any]:
        return {"vector_search_top_k": 999}
