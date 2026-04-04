"""Test HITL Gates functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHitlGates:
    """Test HITL Gates functionality."""

    def test_hitl_gate_imports(self):
        """Test HitlGate module imports."""
        from agentic_core.L5_safety.enforcement.hitl_gate import HitlChoice, HitlDecision, HitlGate
        assert HitlGate is not None
        assert HitlChoice is not None
        assert HitlDecision is not None

    def test_hitl_escalation_imports(self):
        """Test HITL escalation components."""
        from agentic_core.L5_safety.hitl.hitl_escalation_activator import (
            EscalationPriority,
            EscalationRequest,
            HITLEscalationActivator,
        )
        assert HITLEscalationActivator is not None
        assert EscalationRequest is not None
        assert EscalationPriority is not None

    def test_hitl_decision_logger_imports(self):
        """Test HITL decision logger imports."""
        from agentic_core.L5_safety.hitl.decision_logger import HITLDecision, get_decision_logger
        assert HITLDecision is not None
        assert get_decision_logger is not None
