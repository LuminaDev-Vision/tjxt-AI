from typing import Any

from app.agents.base import AbstractAgent
from app.core.prompts import get_prompt
from app.schemas.enums import AgentTypeEnum
from app.tools.course_tools import COURSE_TOOLS, query_course_by_id


class RecommendAgent(AbstractAgent):

    def get_agent_type(self) -> AgentTypeEnum:
        return AgentTypeEnum.RECOMMEND

    def system_message(self) -> str:
        return get_prompt("recommend_agent")

    def tools(self) -> list[dict]:
        return COURSE_TOOLS

    def advisors(self) -> dict[str, Any]:
        return {"vector_search_top_k": 999}
