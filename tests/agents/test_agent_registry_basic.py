from core.agent_registry import AgentRegistry
from profiles.agent_profile import AgentCard
from core.models.models import AgentRole  # normalized import


def test_agent_registry_register_and_lookup():
    registry = AgentRegistry()

    a1 = AgentCard(agent_id="planner-1", role=AgentRole.PLANNER)
    a2 = AgentCard(agent_id="qa-1", role=AgentRole.QA)

    registry.register_agent(a1)
    registry.register_agent(a2)

    assert registry.get_agent("planner-1") is a1
    assert registry.get_agent("qa-1") is a2

    planners = registry.find_agents_by_type("planner")
    assert a1 in planners


def test_agent_registry_find_by_capability():
    registry = AgentRegistry()

    a1 = AgentCard(agent_id="agent-a", role=AgentRole.EXECUTION, capabilities=["write"], agent_type="drafter")
    a2 = AgentCard(agent_id="agent-b", role=AgentRole.EXECUTION, capabilities=["review"], agent_type="qa")

    registry.register_agent(a1)
    registry.register_agent(a2)

    writers = registry.find_agents_by_capability("write")
    assert a1 in writers

