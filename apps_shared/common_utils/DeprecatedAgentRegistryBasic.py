# from archives.legacy_root_folders.orchestration.AgentRegistry import AgentRegistry  # DEPRECATED: Archive import removed to protect archives from validation edits
# from archives.legacy_resume_gen.Agentic_Workflow-10_10.config.agent_profile import AgentCard  # TODO: Fix invalid module name
# from archives.legacy_root_folders.core.models.models import AgentRole  # DEPRECATED: Archive import removed to protect archives from validation edits


def test_agent_registry_register_and_lookup() -> None:
    registry = AgentRegistry()

    a1 = AgentCard(agent_id="planner-1", role=AgentRole.PLANNER)
    a2 = AgentCard(agent_id="qa-1", role=AgentRole.QA)

    registry.register_agent(a1)
    registry.register_agent(a2)

    assert registry.get_agent("planner-1") is a1
    assert registry.get_agent("qa-1") is a2

    planners = registry.find_agents_by_type("planner")
    assert a1 in planners


def test_agent_registry_find_by_capability() -> None:
    registry = AgentRegistry()

    a1 = AgentCard(agent_id="agent-a", role=AgentRole.EXECUTION, capabilities=["write"], agent_type="drafter")
    a2 = AgentCard(agent_id="agent-b", role=AgentRole.EXECUTION, capabilities=["review"], agent_type="qa")

    registry.register_agent(a1)
    registry.register_agent(a2)

    writers = registry.find_agents_by_capability("write")
    assert a1 in writers
