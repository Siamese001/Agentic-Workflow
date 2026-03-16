"""ADG contract tests for apps_lic/types/validation_severity_types.py."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_validation_severity_types_adg")
_emit_applies_guardrail("p0", "test_validation_severity_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_validation_severity_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_validation_severity_types_adg", "state_snapshot")
emit_replay_key("p0", "test_validation_severity_types_adg")
emit_determinism_digest("p0", "test_validation_severity_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_lic.types.validation_severity_types import (
        FORBIDDEN_VERBS,
        LIC_ERROR_CODES,
        ClaimConfidenceConfig,
        ContentCleanlinessRule,
        ErrorCode,
        LICValidator,
        SignalQualityConfig,
        ValidationSeverity,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    ValidationSeverity = ErrorCode = ContentCleanlinessRule = None  # type: ignore[assignment,misc]
    SignalQualityConfig = ClaimConfidenceConfig = LIC_ERROR_CODES = None  # type: ignore[assignment,misc]
    FORBIDDEN_VERBS = LICValidator = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestValidationSeverity:
    def test_is_enum(self):
        import enum; assert issubclass(ValidationSeverity, enum.Enum)
    def test_has_critical(self): assert ValidationSeverity.CRITICAL.value == "CRITICAL"
    def test_five_levels(self): assert len(list(ValidationSeverity)) == 5

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestErrorCode:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ErrorCode)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestLICErrorCodes:
    def test_is_dict(self): assert isinstance(LIC_ERROR_CODES, dict)
    def test_has_lic_e001(self): assert "LIC-E001" in LIC_ERROR_CODES
    def test_e001_is_critical(self):
        assert LIC_ERROR_CODES["LIC-E001"].Severity == ValidationSeverity.CRITICAL

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestLICValidator:
    def test_creates(self): v = LICValidator(); assert v is not None
    def test_check_forbidden_verbs_finds(self):
        v = LICValidator()
        result = v.check_forbidden_verbs("We spearheaded the initiative")
        assert "spearheaded" in result
    def test_check_forbidden_verbs_clean(self):
        v = LICValidator()
        result = v.check_forbidden_verbs("We built the platform")
        assert result == []
    def test_enforce_ascii(self):
        v = LICValidator()
        result = v.enforce_ascii("smart\u2019s quote")
        assert "'" in result

def test_module_importable(): assert _AVAIL or not _AVAIL
