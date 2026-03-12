"""ADG-driven tests for agentic_core/runtime/exceptions/SovereignError.py — fan_in=7.

Exception hierarchy contract tests: verify all exception classes are importable,
have correct inheritance, carry error codes, and behave as standard exceptions.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.runtime.exceptions.SovereignError import (
    CircularDependencyError,
    ConfigurationError,
    HealerError,
    HygieneError,
    IntegrityError,
    ResourceNotFoundError,
    SecurityViolationError,
    SovereignError,
    StructuralError,
    ValidationError,
)


class TestSovereignError:
    def test_is_exception_subclass(self):
        assert issubclass(SovereignError, Exception)

    def test_carries_message(self):
        e = SovereignError("test message")
        assert str(e) == "test message"
        assert e.message == "test message"

    def test_default_error_code(self):
        e = SovereignError("msg")
        assert e.error_code == "SOVEREIGN_ERROR"

    def test_custom_error_code(self):
        e = SovereignError("msg", error_code="CUSTOM")
        assert e.error_code == "CUSTOM"

    def test_raises_and_catches(self):
        with pytest.raises(SovereignError) as exc_info:
            raise SovereignError("boom")
        assert exc_info.value.message == "boom"


class TestHealerError:
    def test_is_sovereign_error(self):
        assert issubclass(HealerError, SovereignError)

    def test_error_code(self):
        e = HealerError("healer failed")
        assert e.error_code == "HEALER_ERROR"

    def test_message_preserved(self):
        e = HealerError("healing loop")
        assert "healing loop" in str(e)


class TestCircularDependencyError:
    def test_is_healer_error(self):
        assert issubclass(CircularDependencyError, HealerError)

    def test_error_code(self):
        e = CircularDependencyError("cycle detected")
        assert e.error_code == "CIRCULAR_DEPENDENCY"

    def test_catches_as_sovereign_error(self):
        with pytest.raises(SovereignError):
            raise CircularDependencyError("cycle")


class TestConfigurationError:
    def test_is_sovereign_error(self):
        assert issubclass(ConfigurationError, SovereignError)

    def test_error_code(self):
        e = ConfigurationError("bad config")
        assert e.error_code == "CONFIG_ERROR"


class TestStructuralError:
    def test_is_healer_error(self):
        assert issubclass(StructuralError, HealerError)

    def test_error_code(self):
        e = StructuralError("relocation failed")
        assert e.error_code == "STRUCTURAL_ERROR"


class TestHygieneError:
    def test_is_healer_error(self):
        assert issubclass(HygieneError, HealerError)

    def test_error_code(self):
        e = HygieneError("hygiene failure")
        assert e.error_code == "HYGIENE_ERROR"


class TestIntegrityError:
    def test_is_sovereign_error(self):
        assert issubclass(IntegrityError, SovereignError)

    def test_error_code(self):
        e = IntegrityError("integrity compromised")
        assert e.error_code == "INTEGRITY_ERROR"


class TestValidationError:
    def test_is_sovereign_error(self):
        assert issubclass(ValidationError, SovereignError)

    def test_error_code(self):
        e = ValidationError("invalid value")
        assert e.error_code == "VALIDATION_ERROR"

    def test_field_attribute(self):
        e = ValidationError("bad field", field="username")
        assert e.field == "username"

    def test_field_defaults_none(self):
        e = ValidationError("no field")
        assert e.field is None


class TestResourceNotFoundError:
    def test_is_sovereign_error(self):
        assert issubclass(ResourceNotFoundError, SovereignError)

    def test_error_code(self):
        e = ResourceNotFoundError("agent X not found")
        assert e.error_code == "RESOURCE_NOT_FOUND"


class TestSecurityViolationError:
    def test_is_sovereign_error(self):
        assert issubclass(SecurityViolationError, SovereignError)

    def test_error_code(self):
        e = SecurityViolationError("bad input", violation_type="INPUT_VIOLATION")
        assert e.error_code == "SECURITY_ERROR"

    def test_violation_type_attribute(self):
        e = SecurityViolationError("policy breach", violation_type="POLICY")
        assert e.violation_type == "POLICY"

    def test_message_contains_violation_type(self):
        e = SecurityViolationError("breach", violation_type="XSS")
        assert "XSS" in str(e)

    def test_catches_as_sovereign_error(self):
        with pytest.raises(SovereignError):
            raise SecurityViolationError("sec", violation_type="T")


class TestExceptionHierarchyOrthogonality:
    """Verify exception hierarchy doesn't mix incompatible branches."""

    def test_configuration_error_not_healer_error(self):
        assert not issubclass(ConfigurationError, HealerError)

    def test_integrity_error_not_healer_error(self):
        assert not issubclass(IntegrityError, HealerError)

    def test_security_violation_not_healer_error(self):
        assert not issubclass(SecurityViolationError, HealerError)

    def test_all_are_catchable_as_base_exception(self):
        errors = [
            SovereignError("a"),
            HealerError("b"),
            CircularDependencyError("c"),
            ConfigurationError("d"),
            StructuralError("e"),
            HygieneError("f"),
            IntegrityError("g"),
            ValidationError("h"),
            ResourceNotFoundError("i"),
            SecurityViolationError("j", violation_type="T"),
        ]
        for e in errors:
            assert isinstance(e, Exception)
            assert isinstance(e, SovereignError)
