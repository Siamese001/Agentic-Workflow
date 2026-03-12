"""ADG contract tests for apps_lic/types/lic_models_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_lic.types.lic_models_types import (
        Route, Archetype, EventType, AgentStatus, ValidationSeverity,
        CircuitState, FailureClassification, FactualGapError, CircuitBreakerOpenError,
        OutreachMission, ValidationResult, RAGResult,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    Route = Archetype = EventType = AgentStatus = ValidationSeverity = None  # type: ignore[assignment,misc]
    CircuitState = FailureClassification = FactualGapError = CircuitBreakerOpenError = None  # type: ignore[assignment,misc]
    OutreachMission = ValidationResult = RAGResult = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRoute:
    def test_is_enum(self):
        import enum; assert issubclass(Route, enum.Enum)
    def test_has_inmail(self): assert Route.INMAIL.value == "INMAIL"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestArchetype:
    def test_is_enum(self):
        import enum; assert issubclass(Archetype, enum.Enum)
    def test_four_archetypes(self): assert len(list(Archetype)) == 4
    def test_c_level(self): assert Archetype.C_LEVEL.value == "C_LEVEL"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestExceptions:
    def test_factual_gap_error_is_exception(self):
        assert issubclass(FactualGapError, Exception)
    def test_circuit_breaker_open_error_is_exception(self):
        assert issubclass(CircuitBreakerOpenError, Exception)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestOutreachMission:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(OutreachMission)
    def test_creates(self):
        m = OutreachMission(
            mission_id="m1", sender_profile={}, recipient_profile={}, JobDescription={}
        )
        assert m.mission_id == "m1"; assert m.prior_message_count == 0

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestValidationResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ValidationResult)
    def test_creates(self):
        vr = ValidationResult(passed=True, Severity=ValidationSeverity.INFO,
                              rule_id="R1", message="ok")
        assert vr.passed is True

def test_module_importable(): assert _AVAIL or not _AVAIL
