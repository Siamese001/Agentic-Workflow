"""Tests for ValidationSeverityConfig with SSOT severity migration."""

import pytest

from agentic_core.L5_safety.config.severity import (
    SeverityLevel,
)
from agentic_core.runtime.config.validation_severity_config import (
    ValidationSeverityConfig,
)


class TestValidationSeverityConfig:
    """Test ValidationSeverityConfig with SSOT."""

    def test_happy_path_critical_severity(self) -> None:
        """Create config with CRITICAL severity from SSOT."""
        config = ValidationSeverityConfig(severity=SeverityLevel.CRITICAL)
        assert config.severity == SeverityLevel.CRITICAL

    def test_happy_path_high_severity(self) -> None:
        """Create config with HIGH severity from SSOT."""
        config = ValidationSeverityConfig(severity=SeverityLevel.HIGH)
        assert config.severity == SeverityLevel.HIGH

    def test_validate_legacy_warning_string(self) -> None:
        """Convert legacy WARNING string to MEDIUM per SSOT mapping."""
        config = ValidationSeverityConfig(severity="WARNING")
        assert config.severity == SeverityLevel.MEDIUM

    def test_validate_legacy_error_string(self) -> None:
        """Convert legacy ERROR string to HIGH per SSOT mapping."""
        config = ValidationSeverityConfig(severity="ERROR")
        assert config.severity == SeverityLevel.HIGH

    def test_validate_lowercase_critical_string(self) -> None:
        """Accept lowercase 'critical' string via from_legacy_string."""
        config = ValidationSeverityConfig(severity="critical")
        assert config.severity == SeverityLevel.CRITICAL

    def test_validate_uppercase_critical_string(self) -> None:
        """Accept uppercase 'CRITICAL' string via from_legacy_string."""
        config = ValidationSeverityConfig(severity="CRITICAL")
        assert config.severity == SeverityLevel.CRITICAL

    def test_validate_invalid_severity_string(self) -> None:
        """Invalid severity string falls back to INFO via from_legacy_string (graceful degradation)."""
        config = ValidationSeverityConfig(severity="INVALID")
        assert config.severity == SeverityLevel.INFO

    def test_validate_none_severity(self) -> None:
        """Reject None severity."""
        with pytest.raises(ValueError, match="Severity is required"):
            ValidationSeverityConfig(severity=None)

    def test_frozen_model_prevents_extra_fields(self) -> None:
        """Reject extra fields due to frozen=True and extra='forbid'."""
        with pytest.raises(Exception):
            ValidationSeverityConfig(
                severity=SeverityLevel.HIGH,
                extra_field="not_allowed",
            )
