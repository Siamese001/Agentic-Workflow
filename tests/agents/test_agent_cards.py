from __future__ import annotations

import pytest

from cognitive_agents import (
    StrategyLLMAgent,
    DraftingGuild,
    SemanticQAAgent,
    ConstitutionalSafetyAgent,
    HYDEQueryAgent,
    QACouncilAgent,
)
from models import AgentCard, AgentRole
from routing import RoutingPolicy
from runtime_utils import SandboxConfig


def _make_agent(agent_cls, card: AgentCard | None = None):
    routing = RoutingPolicy()
    sandbox = SandboxConfig()
    if card is not None:
        return agent_cls(routing_policy=routing, sandbox=sandbox, agent_card=card, meta_profile=None)
    return agent_cls(routing_policy=routing, sandbox=sandbox, meta_profile=None)


def test_all_major_agents_have_agent_card_with_expected_roles():
    agents = [
        (StrategyLLMAgent, AgentRole.PLANNER),
        (DraftingGuild, AgentRole.EXECUTION),
        (SemanticQAAgent, AgentRole.QA),
        (ConstitutionalSafetyAgent, AgentRole.SAFETY),
        (HYDEQueryAgent, AgentRole.META),
        (QACouncilAgent, AgentRole.QA),
    ]

    for cls, expected_role in agents:
        agent = _make_agent(cls)
        assert isinstance(agent.agent_card, AgentCard)
        assert agent.agent_card.role == expected_role
        assert agent.agent_card.agent_id == cls.__name__


def test_allowed_tools_enforced_by_llm_base_agent_helper():
    card = AgentCard(
        agent_id="test_agent",
        role=AgentRole.EXECUTION,
        capabilities=["test"],
        allowed_tools=["tool_a", "tool_b"],
        policy_scope={},
    )

    agent = _make_agent(StrategyLLMAgent, card)

    # Allowed tools should pass silently.
    agent._check_tool_allowed("tool_a")  # type: ignore[attr-defined]
    agent._check_tool_allowed("tool_b")  # type: ignore[attr-defined]

    # Disallowed tool should raise a PermissionError.
    with pytest.raises(PermissionError):
        agent._check_tool_allowed("tool_c")  # type: ignore[attr-defined]
