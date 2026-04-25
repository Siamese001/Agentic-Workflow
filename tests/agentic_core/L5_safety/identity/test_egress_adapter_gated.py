"""Tests for L5_safety/identity/egress_adapter_gated.py."""

import pytest

from agentic_core.L5_safety.identity.egress_adapter_gated import (
    EgressRefused,
    emit_lane_gated_egress,
)
from agentic_core.L5_safety.identity.runtime_entry_sweep import (
    RuntimeLaneDecisionWithSweep,
)


def test_egress_refused_exception_exists():
    """Test that EgressRefused exception exists and can be raised."""
    # Create a minimal mock decision for testing
    mock_decision = type("MockDecision", (), {"final_action": "reject"})()
    
    with pytest.raises(EgressRefused):
        raise EgressRefused(mock_decision)


def test_egress_refused_exception_stores_decision():
    """Test that EgressRefused stores the decision object."""
    mock_decision = type("MockDecision", (), {"final_action": "reject"})()
    
    exception = EgressRefused(mock_decision)
    assert exception.decision is mock_decision
    assert "EgressRefused: final_action=reject" in str(exception)


def test_emit_lane_gated_egress_function_exists():
    """Test that emit_lane_gated_egress function exists and can be imported."""
    assert emit_lane_gated_egress is not None
