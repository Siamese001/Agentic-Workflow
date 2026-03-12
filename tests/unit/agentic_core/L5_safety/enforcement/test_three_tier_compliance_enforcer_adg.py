"""ADG-driven tests for L5_safety/enforcement/three_tier_compliance_enforcer.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.enforcement.three_tier_compliance_enforcer import (
    GUARDIAN_TEST_PATTERNS,
    CONTRACT_HOOKS,
    TierStatus,
    AgentCompliance,
    ComplianceResult,
)
from agentic_core.L5_safety.enforcement.registry_verification_enforcer import AgentInfo


class TestConstants:
    def test_guardian_test_patterns_list(self):
        assert isinstance(GUARDIAN_TEST_PATTERNS, list)
        assert len(GUARDIAN_TEST_PATTERNS) > 0

    def test_contract_hooks_dict(self):
        assert isinstance(CONTRACT_HOOKS, dict)
        assert "ruff" in CONTRACT_HOOKS


class TestTierStatus:
    def test_creates(self):
        t = TierStatus(tier_name="Contract", is_covered=True)
        assert t.tier_name == "Contract"
        assert t.is_covered is True

    def test_defaults(self):
        t = TierStatus(tier_name="Soul", is_covered=False)
        assert t.coverage_type == ""
        assert t.details == []
        assert t.gaps == []


class TestAgentCompliance:
    def _make_agent_info(self):
        from pathlib import Path
        return AgentInfo(
            class_name="FooAgent",
            file_path=Path("agentic_core/L1_cognition/FooAgent.py"),
            relative_path="agentic_core/L1_cognition/FooAgent.py",
            layer="L1_cognition",
        )

    def test_creates(self):
        ac = AgentCompliance(agent=self._make_agent_info())
        assert ac is not None

    def test_all_uncovered_score_zero(self):
        ac = AgentCompliance(agent=self._make_agent_info())
        assert ac.compliance_score == 0

    def test_one_tier_covered_score_one(self):
        ac = AgentCompliance(agent=self._make_agent_info())
        ac.contract_tier = TierStatus("Contract", is_covered=True)
        assert ac.compliance_score == 1

    def test_fully_compliant_requires_all_three(self):
        ac = AgentCompliance(agent=self._make_agent_info())
        ac.contract_tier = TierStatus("Contract", is_covered=True)
        ac.blueprint_tier = TierStatus("Blueprint", is_covered=True)
        ac.soul_tier = TierStatus("Soul", is_covered=True)
        assert ac.is_fully_compliant is True
        assert ac.compliance_score == 3


class TestComplianceResult:
    def test_creates_with_defaults(self):
        r = ComplianceResult()
        assert r.total_agents == 0
        assert r.fully_compliant == 0
        assert r.agent_compliance == []
