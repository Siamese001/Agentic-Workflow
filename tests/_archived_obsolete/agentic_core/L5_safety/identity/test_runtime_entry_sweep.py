"""Tests for L5_safety/identity/runtime_entry_sweep.py."""

import pytest

from agentic_core.L5_safety.identity.runtime_entry_sweep import (
    RuntimeLaneDecisionWithSweep,
    RuntimeLaneRejected,
    evaluate_runtime_lane_with_sweep,
)


def test_evaluate_runtime_lane_with_sweep_function_exists():
    """Test that evaluate_runtime_lane_with_sweep function exists and can be imported."""
    assert evaluate_runtime_lane_with_sweep is not None


def test_runtime_lane_rejected_exception_exists():
    """Test that RuntimeLaneRejected exception exists and can be raised."""
    # Create a minimal mock decision for testing
    mock_decision = type("MockDecision", (), {"final_action": "reject"})()
    
    with pytest.raises(RuntimeLaneRejected):
        raise RuntimeLaneRejected(mock_decision)


def test_runtime_lane_decision_with_sweep_exists():
    """Test that RuntimeLaneDecisionWithSweep dataclass exists."""
    assert RuntimeLaneDecisionWithSweep is not None
