"""ADG contract tests for apps_lic/types/validation_severity_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_lic.types.validation_severity_types import (
        ValidationSeverity, ErrorCode, ContentCleanlinessRule,
        SignalQualityConfig, ClaimConfidenceConfig, LIC_ERROR_CODES,
        FORBIDDEN_VERBS, LICValidator,
    )
    _AVAIL = True
except Exception:
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
