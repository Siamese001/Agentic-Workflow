"""ADG contract tests for runtime/types/recovery_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
from agentic_core.runtime.types.recovery_types import (
    RecoveryStrategy, ResilienceError, TransientError, PermanentError, RetryExhaustedError,
)

class TestRecoveryStrategy:
    def test_is_enum(self):
        import enum; assert issubclass(RecoveryStrategy, enum.Enum)

class TestResilienceError:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ResilienceError)
    def test_creates(self):
        e = ResilienceError(_message="oops", _code="ERR_001")
        assert e._message == "oops"; assert e._code == "ERR_001"

class TestTransientError:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(TransientError)
    def test_creates(self):
        e = TransientError(_message="retry", _code="TRANSIENT"); assert e._message == "retry"

class TestRetryExhaustedError:
    def test_creates_with_attempts(self):
        e = RetryExhaustedError(_message="exhausted", _code="EXHAUSTED", _attempts=3)
        assert e._attempts == 3
