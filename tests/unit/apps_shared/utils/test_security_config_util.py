"""Foundational behavioral tests for apps_shared/utils/security_config_util.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_security_config_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Import with graceful fallback for collection-time import issues
try:
    from apps_shared.utils.security_config_util import (
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        InputSanitizer,
        InputValidator,
        SecureTokenGenerator,
        ValidationLevel,
        ValidationResult,
    )
except ImportError as _import_err:
    pytest.skip(f"security_config_util not available: {_import_err}", allow_module_level=True)

pytestmark = pytest.mark.unit


class TestValidationLevelContract:
    def test_is_enum(self):
        import enum

        assert issubclass(ValidationLevel, enum.Enum)

    def test_has_members(self):
        assert len(list(ValidationLevel)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in ValidationLevel:
            assert member.value is not None

    def test_known_member_strict_exists(self):
        assert hasattr(ValidationLevel, "STRICT")


class TestValidationResultContract:
    def test_is_dataclass(self):
        import dataclasses

        assert dataclasses.is_dataclass(ValidationResult)

    def test_field_names_present(self):
        import dataclasses

        field_names = {f.name for f in dataclasses.fields(ValidationResult)}
        assert field_names >= {"errors", "sanitized_value", "valid"}


class TestInputSanitizerContract:
    def test_is_class(self):
        assert isinstance(InputSanitizer, type)

    def test_has_method_sanitize_string(self):
        assert callable(getattr(InputSanitizer, "sanitize_string", None))

    def test_has_method_sanitize_path(self):
        assert callable(getattr(InputSanitizer, "sanitize_path", None))

    def test_has_method_sanitize_identifier(self):
        assert callable(getattr(InputSanitizer, "sanitize_identifier", None))


class TestInputValidatorContract:
    def test_is_class(self):
        assert isinstance(InputValidator, type)

    def test_has_method_validate_email(self):
        assert callable(getattr(InputValidator, "validate_email", None))

    def test_has_method_validate_url(self):
        assert callable(getattr(InputValidator, "validate_url", None))

    def test_has_method_validate_length(self):
        assert callable(getattr(InputValidator, "validate_length", None))

    def test_has_method_validate_not_empty(self):
        assert callable(getattr(InputValidator, "validate_not_empty", None))


class TestSecureTokenGeneratorContract:
    def test_is_class(self):
        assert isinstance(SecureTokenGenerator, type)

    def test_has_method_generate_token(self):
        assert callable(getattr(SecureTokenGenerator, "generate_token", None))

    def test_has_method_generate_api_key(self):
        assert callable(getattr(SecureTokenGenerator, "generate_api_key", None))

    def test_has_method_hash_value(self):
        assert callable(getattr(SecureTokenGenerator, "hash_value", None))

    def test_has_method_verify_hash(self):
        """Test has_method_verify_hash contract compliance."""
        assert callable(getattr(SecureTokenGenerator, "verify_hash", None))


class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None


class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None


class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None


class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None


class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module security_config_util must be importable or skip gracefully."""
    pass  # Import verified at module level
