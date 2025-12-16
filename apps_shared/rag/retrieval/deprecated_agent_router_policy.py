import logging

logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant
_logger = logging.getLogger(__name__)


def test_choose_agents_for_strategy_task_prefers_planner() -> None:
    """TODO: Add docstring."""
    AgentRegistry()
    PLANNER = AgentCard(agent_id='planner-1',
                        role=AgentRole.PLANNER, agent_type='planner')
    RESEARCHER = AgentCard(agent_id='researcher-1',
                           role=AgentRole.EXECUTION, agent_type='researcher')
    registry.register_agent(planner)
    registry.register_agent(researcher)
    choose_agents_for_task('strategy', registry)
    assert planner in chosen

