"""Tests for phase-hardened L5SafetyBase fail-closed behaviors."""

from pathlib import Path

import pytest

from agentic_core.base_agents.L5SafetyBase import L5SafetyBase


@pytest.mark.unit
class TestL5SafetyBaseHardening:
    """Behavioral coverage for phase-hardened L5SafetyBase fail-closed defaults."""

    def test_validate_is_fail_closed(self):
        """Happy: validate() returns valid=False with override message and correct target_type."""
        agent = L5SafetyBase()
        result = agent.validate("any_target")
        assert result["valid"] is False
        assert "must be overridden" in result["violations"][0]
        assert result["target_type"] == "str"

    def test_enforce_guardrail_is_fail_closed(self):
        """Failure: enforce_guardrail() returns False regardless of guardrail name or context."""
        agent = L5SafetyBase()
        assert agent.enforce_guardrail("critical_boundary", {"user": "admin"}) is False

    def test_check_gravity_is_fail_closed(self):
        """Edge: check_gravity() returns compliant=False and path as string."""
        agent = L5SafetyBase()
        p = Path("/some/path")
        result = agent.check_gravity(p)
        assert result["compliant"] is False
        assert "must be overridden" in result["violations"][0]
        assert str(p) in result["path"]
