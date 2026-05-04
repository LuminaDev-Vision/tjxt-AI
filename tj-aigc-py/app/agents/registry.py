from app.agents.base import AbstractAgent
from app.schemas.enums import AgentTypeEnum

_registry: dict[AgentTypeEnum, AbstractAgent] = {}


def register(agent: AbstractAgent):
    _registry[agent.get_agent_type()] = agent


def get_agent(agent_type: AgentTypeEnum) -> AbstractAgent | None:
    return _registry.get(agent_type)


def get_all_agents() -> dict[AgentTypeEnum, AbstractAgent]:
    return dict(_registry)


def init_agents():
    from app.agents.buy_agent import BuyAgent
    from app.agents.consult_agent import ConsultAgent
    from app.agents.knowledge_agent import KnowledgeAgent
    from app.agents.recommend_agent import RecommendAgent
    from app.agents.route_agent import RouteAgent

    for cls in [RouteAgent, RecommendAgent, ConsultAgent, BuyAgent, KnowledgeAgent]:
        register(cls())
