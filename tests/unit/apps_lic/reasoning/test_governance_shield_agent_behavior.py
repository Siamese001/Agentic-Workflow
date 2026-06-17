"""Behavioral tests for apps_lic/reasoning/GovernanceShieldAgent.py.

The live shield is deterministic and no longer exposes any Qwen/local-provider
path. These tests pin the governed surface: evaluate(), audit_outreach(),
generate_safety_protocol(), and analyze_governance().
"""

from __future__ import annotations

import asyncio
import dataclasses

import pytest

from apps_lic.reasoning.GovernanceShieldAgent import (
    GovernanceShieldAgent,
    RiskLevel,
    RiskProfile,
    SafetyProtocol,
    create_governance_shield_agent,
)

pytestmark = pytest.mark.unit


def _bare_agent() -> GovernanceShieldAgent:
    """Construct a minimal agent without triggering LICAgentBase dependencies."""
    agent = object.__new__(GovernanceShieldAgent)
    agent.naive_patterns = {
        "absolute_accuracy": (
            "100% accurate",
            "perfect accuracy",
            "always correct",
        ),
        "unsupported_claims": (
            "guaranteed",
            "revolutionary",
        ),
        "sales_pitch": (
            "synergies",
        ),
    }
    return agent


class TestGovernanceShieldAgentSurface:
    def test_agent_is_dataclass_and_factory_is_callable(self) -> None:
        assert dataclasses.is_dataclass(GovernanceShieldAgent)
        assert callable(create_governance_shield_agent)


class TestGovernanceShieldAgentDeterministicBehavior:
    def test_evaluate_flags_naive_claims_and_recommends_rewrite(self) -> None:
        agent = _bare_agent()

        result = agent.evaluate("We have 100% accurate AI with revolutionary synergies.")

        assert result["passed"] is False
        assert result["risk_level"] == RiskLevel.HIGH.value
        assert {"absolute_accuracy", "unsupported_claims", "sales_pitch"} & set(
            result["flags"]
        )
        assert "100% accurate" not in result["recommended_text"]
        assert "synergies" not in result["recommended_text"].lower()

    def test_audit_outreach_rewrites_salesy_phrases(self) -> None:
        agent = _bare_agent()

        text = agent.audit_outreach("We have 100% accurate AI and synergies.")

        assert isinstance(text, str)
        assert text
        assert "100% accurate" not in text
        assert "synergies" not in text.lower()

    def test_generate_safety_protocol_blocks_high_risk_only(self) -> None:
        agent = _bare_agent()

        high = agent.generate_safety_protocol(
            RiskProfile(level=RiskLevel.HIGH, flags=("absolute_accuracy",))
        )
        low = agent.generate_safety_protocol(
            RiskProfile(level=RiskLevel.LOW, flags=())
        )

        assert isinstance(high, SafetyProtocol)
        assert high.blocked is True
        assert "block_until_evidence_review" in high.controls
        assert low.blocked is False
        assert "block_until_evidence_review" not in low.controls

    def test_analyze_governance_wraps_deterministic_evaluate(self) -> None:
        agent = _bare_agent()

        result = asyncio.run(agent.analyze_governance("We are perfect and guaranteed."))

        assert result["success"] is True
        assert result["model_used"] == "deterministic_governance_shield"
        assert result["latency_ms"] == 0.0
        assert result["analysis"]["passed"] is False
        assert result["analysis"]["risk_level"] == RiskLevel.HIGH.value
