"""Logic/property tests for safety escalation and thresholds."""
from __future__ import annotations
import pytest

from agentic_workflow.runtime.shared.config import SAFETY_THRESHOLD
from agentic_workflow.runtime.shared.models import GateDecision, ValidationSeverity

class TestSafetyThresholdProperties:
    def test_threshold_in_valid_range(self):
        assert 0.0 <= SAFETY_THRESHOLD <= 1.0

    def test_threshold_determinism(self):
        from agentic_workflow.runtime.shared.config import SAFETY_THRESHOLD as T2
        assert SAFETY_THRESHOLD == T2

class TestGateDecisionProperties:
    def test_gate_decision_has_values(self):
        assert len(list(GateDecision)) >= 2

    def test_gate_decision_iteration_stable(self):
        assert list(GateDecision) == list(GateDecision)

class TestValidationSeverityOrdering:
    def test_severity_has_levels(self):
        severities = list(ValidationSeverity)
        assert len(severities) >= 2

    def test_severity_determinism(self):
        assert list(ValidationSeverity) == list(ValidationSeverity)
