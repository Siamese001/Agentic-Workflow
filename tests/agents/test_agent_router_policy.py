from core.agent_registry import AgentRegistry
from core.agent_router_policy import choose_agents_for_task
from profiles.agent_profile import AgentCard
from models import AgentRole


def test_choose_agents_for_strategy_task_prefers_planner():
    registry = AgentRegistry()

    planner = AgentCard(agent_id="planner-1", role=AgentRole.PLANNER, agent_type="planner")
    researcher = AgentCard(agent_id="researcher-1", role=AgentRole.EXECUTION, agent_type="researcher")

    registry.register_agent(planner)
    registry.register_agent(researcher)

    chosen = choose_agents_for_task("strategy", registry)
    assert planner in chosen
