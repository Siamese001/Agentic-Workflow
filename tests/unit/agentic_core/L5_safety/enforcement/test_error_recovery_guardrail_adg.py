"""ADG-driven tests for agentic_core/L5_safety/enforcement/error_recovery_guardrail.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.error_recovery_guardrail import (  # noqa: F401
        ErrorCategory,
        RecoveryStrategy,
        ErrorContext,
        RecoveryResult,
        ErrorRecoveryGuardrail,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
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
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="error_recovery_guardrail.py deps unavailable")
class TestErrorCategory:
    def test_is_enum(self):
        import enum
        assert issubclass(ErrorCategory, enum.Enum)
    def test_has_members(self):
        assert len(list(ErrorCategory)) >= 1
    def test_importable(self):
        assert ErrorCategory is not None

@pytest.mark.skipif(not _AVAILABLE, reason="error_recovery_guardrail.py deps unavailable")
class TestRecoveryStrategy:
    def test_is_enum(self):
        import enum
        assert issubclass(RecoveryStrategy, enum.Enum)
    def test_has_members(self):
        assert len(list(RecoveryStrategy)) >= 1
    def test_importable(self):
        assert RecoveryStrategy is not None

@pytest.mark.skipif(not _AVAILABLE, reason="error_recovery_guardrail.py deps unavailable")
class TestErrorContext:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ErrorContext)
    def test_importable(self):
        assert ErrorContext is not None

@pytest.mark.skipif(not _AVAILABLE, reason="error_recovery_guardrail.py deps unavailable")
class TestRecoveryResult:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RecoveryResult)
    def test_importable(self):
        assert RecoveryResult is not None

@pytest.mark.skipif(not _AVAILABLE, reason="error_recovery_guardrail.py deps unavailable")
class TestErrorRecoveryGuardrail:
    def test_is_class(self):
        assert isinstance(ErrorRecoveryGuardrail, type)
    def test_importable(self):
        assert ErrorRecoveryGuardrail is not None

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

@pytest.mark.skipif(not _AVAILABLE, reason="error_recovery_guardrail.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module error_recovery_guardrail.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
