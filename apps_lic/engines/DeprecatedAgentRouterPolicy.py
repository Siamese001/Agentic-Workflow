# from archives.legacy_root_folders.orchestration.AgentRegistry import AgentRegistry  # DEPRECATED: Archive import removed to protect archives from validation edits
# from archives.legacy_root_folders.core.agent_router_policy import choose_agents_for_task  # DEPRECATED: Archive import removed to protect archives from validation edits
# from archives.legacy_resume_gen.Agentic_Workflow-10_10.config.agent_profile import AgentCard  # TODO: Fix invalid module name
# from archives.legacy_root_folders.core.models.models import AgentRole  # DEPRECATED: Archive import removed to protect archives from validation edits


def test_choose_agents_for_strategy_task_prefers_planner() -> None:
    registry = AgentRegistry()

    planner = AgentCard(agent_id="planner-1", role=AgentRole.PLANNER, agent_type="planner")
    researcher = AgentCard(agent_id="researcher-1", role=AgentRole.EXECUTION, agent_type="researcher")

    registry.register_agent(planner)
    registry.register_agent(researcher)

    chosen = choose_agents_for_task("strategy", registry)
    assert planner in chosen
