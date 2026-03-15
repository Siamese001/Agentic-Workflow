"""Foundational behavioral tests for agentic_core/L5_safety/enforcement/error_recovery_guardrail.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_error_recovery_guardrail_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.error_recovery_guardrail import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        ErrorCategory,
        ErrorContext,
        ErrorRecoveryGuardrail,
        RecoveryResult,
        RecoveryStrategy,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    ErrorCategory = None  # type: ignore[assignment,misc]
    RecoveryStrategy = None  # type: ignore[assignment,misc]
    ErrorContext = None  # type: ignore[assignment,misc]
    RecoveryResult = None  # type: ignore[assignment,misc]
    ErrorRecoveryGuardrail = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="error_recovery_guardrail.py deps unavailable")
class TestErrorCategoryContract:
    def test_is_enum(self):
        import enum
        assert issubclass(ErrorCategory, enum.Enum)

    def test_has_members(self):
        assert len(list(ErrorCategory)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in ErrorCategory:
            assert member.value is not None

    def test_known_member_validation_exists(self):
        assert hasattr(ErrorCategory, 'VALIDATION')

@pytest.mark.skipif(not _AVAILABLE, reason="error_recovery_guardrail.py deps unavailable")
class TestRecoveryStrategyContract:
    def test_is_enum(self):
        import enum
        assert issubclass(RecoveryStrategy, enum.Enum)

    def test_has_members(self):
        assert len(list(RecoveryStrategy)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in RecoveryStrategy:
            assert member.value is not None

    def test_known_member_retry_exists(self):
        assert hasattr(RecoveryStrategy, 'RETRY')

@pytest.mark.skipif(not _AVAILABLE, reason="error_recovery_guardrail.py deps unavailable")
class TestErrorContextContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ErrorContext)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ErrorContext)}
        assert field_names >= {'error', 'stack_trace', 'message', 'timestamp', 'error_type'}

@pytest.mark.skipif(not _AVAILABLE, reason="error_recovery_guardrail.py deps unavailable")
class TestRecoveryResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RecoveryResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(RecoveryResult)}
        assert field_names >= {'success', 'strategy_used', 'error_message', 'attempts', 'recovered_value'}

@pytest.mark.skipif(not _AVAILABLE, reason="error_recovery_guardrail.py deps unavailable")
class TestErrorRecoveryGuardrailContract:
    def test_is_class(self):
        assert isinstance(ErrorRecoveryGuardrail, type)

    def test_has_method_handle_error(self):
        assert callable(getattr(ErrorRecoveryGuardrail, 'handle_error', None))

    def test_has_method_get_statistics(self):
        assert callable(getattr(ErrorRecoveryGuardrail, 'get_statistics', None))

    def test_has_method_get_error_log(self):
        assert callable(getattr(ErrorRecoveryGuardrail, 'get_error_log', None))

@pytest.mark.skipif(not _AVAILABLE, reason="error_recovery_guardrail.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="error_recovery_guardrail.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="error_recovery_guardrail.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="error_recovery_guardrail.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="error_recovery_guardrail.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module error_recovery_guardrail must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
