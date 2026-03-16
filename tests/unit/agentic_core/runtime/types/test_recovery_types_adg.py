"""ADG contract tests for runtime/types/recovery_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_recovery_types_adg")
_emit_applies_guardrail("p0", "test_recovery_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_recovery_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_recovery_types_adg", "state_snapshot")
emit_replay_key("p0", "test_recovery_types_adg")
emit_determinism_digest("p0", "test_recovery_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
pytestmark = pytest.mark.unit
from agentic_core.runtime.types.recovery_types import (
    RecoveryStrategy,
    ResilienceError,
    RetryExhaustedError,
    TransientError,
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
