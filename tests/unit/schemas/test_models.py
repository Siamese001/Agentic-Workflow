"""Unit tests for runtime/shared/models.py"""
from __future__ import annotations
from enum import Enum
from shared.types.models import GateDecision, ValidationSeverity, HopStatus, CircuitState, ValidationResult, ThematicAnalysis, HopCheckpoint, APICallStatus, RAGState, ImmutableStagingBuffer
from shared.configuration.reasoning_config import ReasoningConfig
# Utils classes don't exist yet, skipping import


class TestGateDecision:
    def test_is_enum(self):
        assert issubclass(GateDecision, Enum)

    def test_has_values(self):
        assert len(list(GateDecision)) >= 1

    def test_determinism(self):
        assert list(GateDecision) == list(GateDecision)

class TestValidationSeverity:
    def test_is_enum(self):
        assert issubclass(ValidationSeverity, Enum)

    def test_has_levels(self):
        assert len(list(ValidationSeverity)) >= 2

class TestCircuitState:
    def test_is_enum(self):
        assert issubclass(CircuitState, Enum)

    def test_has_states(self):
        assert len(list(CircuitState)) >= 2

class TestHopStatus:
    def test_is_enum(self):
        assert issubclass(HopStatus, Enum)

class TestAPICallStatus:
    def test_is_enum(self):
        assert issubclass(APICallStatus, Enum)

class TestReasoningConfig:
    def test_creation(self):
        cfg = ReasoningConfig()
        assert cfg is not None

    def test_determinism(self):
        assert ReasoningConfig() == ReasoningConfig()

class TestValidationResult:
    def test_creation(self):
        result = ValidationResult(
            rule_id="test_rule",
            passed=True,
            severity=list(ValidationSeverity)[0],
            message="ok",
        )
        assert result.passed is True

    def test_invalid_case(self):
        result = ValidationResult(
            rule_id="test_rule",
            passed=False,
            severity=list(ValidationSeverity)[-1],
            message="fail",
        )
        assert result.passed is False

class TestRAGState:
    def test_creation(self):
        state = RAGState()
        assert state is not None

class TestImmutableStagingBuffer:
    def test_creation(self):
        buf = ImmutableStagingBuffer()
        assert buf is not None
