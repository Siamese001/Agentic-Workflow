"""Tests for L5_safety/identity/action_pipeline.py."""

import pytest

from agentic_core.L5_safety.identity.action_pipeline import (
    V4ActionOutcome,
    run_v4_action,
)
from agentic_core.L5_safety.identity.runtime_entry_sweep import (
    RuntimeLaneDecisionWithSweep,
)


def test_run_v4_action_function_exists():
    """Test that run_v4_action function exists and can be imported."""
    assert run_v4_action is not None


def test_v4_action_outcome_exists():
    """Test that V4ActionOutcome dataclass exists."""
    assert V4ActionOutcome is not None


def test_v4_action_outcome_allowed_property():
    """Test that V4ActionOutcome.allowed property returns True when decision allows."""
    # Create a minimal mock decision
    mock_decision = type("MockDecision", (), {"final_action": "allow"})()
    
    outcome = V4ActionOutcome(
        decision=mock_decision,
        write_v3_key="test_key",
        write_attached=None,
        egresses=(),
        audit_record=None,
    )
    
    assert outcome.allowed is True


def test_v4_action_outcome_allowed_property_false_on_reject():
    """Test that V4ActionOutcome.allowed property returns False when decision rejects."""
    # Create a minimal mock decision
    mock_decision = type("MockDecision", (), {"final_action": "reject"})()
    
    outcome = V4ActionOutcome(
        decision=mock_decision,
        write_v3_key=None,
        write_attached=None,
        egresses=(),
        audit_record=None,
    )
    
    assert outcome.allowed is False
