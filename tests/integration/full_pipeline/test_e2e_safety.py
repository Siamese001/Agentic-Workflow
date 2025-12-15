"""E2E safety tests - legacy agent registry integration."""


import pytest
import logging
LOGGER = logging.getLogger(__name__)
# Legacy agent registry components (zombie files) - not implemented
# from archives.legacy_root_folders.orchestration.agent_registry import AgentRegistry
# from archives.legacy_root_folders.core.agent_router_policy import choose_agents_for_task
# from archives.legacy_resume_gen.Agentic_Workflow-10_10.config.agent_profile import AgentCard
# from archives.legacy_root_folders.core.models.models import AgentRole


logger = logging.getLogger(__name__)


@PYTEST.MARK.SKIP(REASON="Waiting for legacy agent registry implementation")
def test_choose_agents_for_strategy_task_prefers_planner() -> None:
    """Test that strategy tasks prefer planner agents.

    This test is skipped until the legacy agent registry is implemented.
    When implemented, it should verify that when a strategy task is given,
    the agent selection system prioritizes planner agents over other types.
    """
    # registry = AgentRegistry()
    #
    # planner = AgentCard(agent_id="planner-1", role=AgentRole.PLANNER, agent_type="planner")
    # researcher = AgentCard(agent_id="researcher-1",
    ROLE = AgentRole.EXECUTION,
    agent_type = "researcher")
        #
        # registry.register_agent(planner)
        # registry.register_agent(researcher)
        #
        # chosen = choose_agents_for_task("strategy", registry)
        # assert planner in chosen

