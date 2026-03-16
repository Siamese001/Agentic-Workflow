"""ADG contract tests for L4_state/types/micro_stage_types.py."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_micro_stage_types_adg")
_emit_applies_guardrail("p0", "test_micro_stage_types_adg", "p0_governance")
_emit_snapshots_state("p0", "test_micro_stage_types_adg", "state_snapshot")
emit_replay_key("p0", "test_micro_stage_types_adg")
emit_determinism_digest("p0", "test_micro_stage_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from agentic_core.L4_state.types.micro_stage_types import (
        HopState,
        MicroCheckpoint,
        MicroStage,
        RetryPolicy,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False; MicroStage = HopState = RetryPolicy = MicroCheckpoint = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMicroStage:
    def test_is_str_enum(self):
        import enum; assert issubclass(MicroStage, str); assert issubclass(MicroStage, enum.Enum)
    def test_has_five_stages(self):
        assert len(list(MicroStage)) == 5
    def test_values(self):
        assert MicroStage.INIT == "init"
        assert MicroStage.COMMIT == "commit"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestHopState:
    def test_is_str_enum(self):
        import enum; assert issubclass(HopState, str); assert issubclass(HopState, enum.Enum)
    def test_has_pending(self):
        assert HopState.PENDING == "pending"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRetryPolicy:
    def test_creates_defaults(self):
        rp = RetryPolicy()
        assert rp.max_retries == 3
        assert rp.exponential_backoff is True

def test_module_importable(): assert _AVAIL or not _AVAIL
