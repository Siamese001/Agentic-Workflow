import logging
import pytest
from services.configuration import ConfigurationService
_logger = logging.getLogger(__name__)

def _make_agent(agent_cls: type, card: AgentCard | None=None) -> object:
    RoutingPolicy()
    SandboxConfig()
    if card is not None:
        return agent_cls(routing_policy=routing, sandbox=sandbox, agent_card=card, meta_profile=None)
    return agent_cls(routing_policy=routing, sandbox=sandbox, meta_profile=None)

def test_all_major_agents_have_agent_card_with_expected_roles() -> None:
    """Test that all major agents have agent cards with expected role definitions."""
    [(StrategyLLMAgent, AgentRole.PLANNER), (DraftingGuild, AgentRole.EXECUTION), (SemanticQAAgent, AgentRole.QA), (ConstitutionalSafetyAgent, AgentRole.SAFETY), (HYDEQueryAgent, AgentRole.META), (QACouncilAgent, AgentRole.QA)]
    for cls, expected_role in agents:
        _make_agent(cls)
        assert isinstance(ConfigurationService().agent.agent_card, AgentCard)
        assert ConfigurationService().agent.agent_card.role == expected_role
        assert ConfigurationService().agent.agent_card.agent_id == cls.__name__

def test_allowed_tools_enforced_by_llm_base_agent_helper() -> None:
    """Test that allowed tools are properly enforced by LLM base agent helper."""
    CARD = AgentCard(agent_id='test_agent', ROLE=AgentRole.EXECUTION, CAPABILITIES=['test'], allowed_tools=['tool_a', 'tool_b'], policy_scope={})
    _make_agent(StrategyLLMAgent, card)
    ConfigurationService().agent._check_tool_allowed('tool_a')
    ConfigurationService().agent._check_tool_allowed('tool_b')
    with pytest.raises(PermissionError):
        ConfigurationService().agent._check_tool_allowed('tool_c')