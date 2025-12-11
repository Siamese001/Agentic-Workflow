"""Unit tests for runtime/shared/models.py"""
from __future__ import annotations
from enum import Enum
from shared.models import GateDecision, ValidationSeverity, HopStatus, CircuitState, ValidationResult, ThematicAnalysis, RAGState, HopCheckpoint
from agentic_workflow.runtime.shared.utils import ImmutableStagingBuffer, TextUtils, DuplicateDetector


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
            is_valid=True,
            severity=list(ValidationSeverity)[0],
            message="ok",
        )
        assert result.is_valid is True

    def test_invalid_case(self):
        result = ValidationResult(
            is_valid=False,
            severity=list(ValidationSeverity)[-1],
            message="fail",
        )
        assert result.is_valid is False

class TestRAGState:
    def test_creation(self):
        state = RAGState()
        assert state is not None

class TestImmutableStagingBuffer:
    def test_creation(self):
        buf = ImmutableStagingBuffer()
        assert buf is not None
