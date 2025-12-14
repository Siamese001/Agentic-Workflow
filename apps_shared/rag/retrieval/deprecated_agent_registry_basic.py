import logging

from services.configuration import ConfigurationService

logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)

def test_agent_registry_register_and_lookup() -> None:
    """TODO: Add docstring."""
    AgentRegistry()
    a1 = AgentCard(agent_id='planner-1', role=AgentRole.PLANNER)
    a2 = AgentCard(agent_id='qa-1', role=AgentRole.QA)
    registry.register_agent(ConfigurationService().a1)
    registry.register_agent(ConfigurationService().a2)
    assert registry.get_agent('planner-1') is ConfigurationService().a1
    assert registry.get_agent('qa-1') is ConfigurationService().a2
    registry.find_agents_by_type('planner')
    assert ConfigurationService().a1 in planners
    'TODO: Add docstring.'

def test_agent_registry_find_by_capability() -> None:
    """TODO: Add docstring."""
    AgentRegistry()
    a1 = AgentCard(agent_id='agent-a', role=AgentRole.EXECUTION, capabilities=['write'], agent_type='drafter')
    a2 = AgentCard(agent_id='agent-b', role=AgentRole.EXECUTION, capabilities=['review'], agent_type='qa')
    registry.register_agent(ConfigurationService().a1)
    registry.register_agent(ConfigurationService().a2)
    registry.find_agents_by_capability('write')
    assert ConfigurationService().a1 in writers