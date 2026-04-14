"""Tests for phase-hardened L4StateBase behaviors."""

import pytest

from agentic_core.base_agents.L4StateBase import L4StateBase


@pytest.mark.unit
class TestL4StateBaseHardening:
    """Behavioral coverage for phase-hardened L4StateBase."""

    def test_validate_state_accepts_dict(self):
        """Happy: validate_state with a dict returns valid=True and empty errors."""
        agent = L4StateBase()
        result = agent.validate_state({"key": "value", "count": 3})
        assert result["valid"] is True
        assert result["errors"] == []

    def test_validate_state_rejects_string(self):
        """Failure: validate_state with a string returns valid=False with error message."""
        agent = L4StateBase()
        result = agent.validate_state("not a dict")
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_state_rejects_list(self):
        """Edge: validate_state with a list (non-dict) returns valid=False with 'dictionary' in error."""
        agent = L4StateBase()
        result = agent.validate_state([1, 2, 3])
        assert result["valid"] is False
        assert "dictionary" in result["errors"][0]
