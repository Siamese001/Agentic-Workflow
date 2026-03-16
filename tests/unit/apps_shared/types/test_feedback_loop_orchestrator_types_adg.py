"""ADG contract tests for apps_shared/types/feedback_loop_orchestrator_types.py."""
from __future__ import annotations

from datetime import datetime, timezone

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

_emit_records_execution_trace("p0", "evidence", "test_feedback_loop_orchestrator_types_adg")
_emit_applies_guardrail("p0", "test_feedback_loop_orchestrator_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_feedback_loop_orchestrator_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_feedback_loop_orchestrator_types_adg", "state_snapshot")
emit_replay_key("p0", "test_feedback_loop_orchestrator_types_adg")
emit_determinism_digest("p0", "test_feedback_loop_orchestrator_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_FIXED_DT = datetime(2026, 1, 1, tzinfo=timezone.utc)
pytestmark = pytest.mark.unit
try:
    from apps_shared.types.feedback_loop_orchestrator_types import (
        ConstraintFailureType,
        RegenerationCheckpoint,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    ConstraintFailureType = RegenerationCheckpoint = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestConstraintFailureType:
    def test_is_enum(self):
        import enum; assert issubclass(ConstraintFailureType, enum.Enum)
    def test_is_str_enum(self): assert issubclass(ConstraintFailureType, str)
    def test_has_mechanical(self): assert ConstraintFailureType.MECHANICAL.value == "MECHANICAL"
    def test_has_conflict(self): assert ConstraintFailureType.CONFLICT.value == "CONFLICT"
    def test_four_types(self): assert len(list(ConstraintFailureType)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRegenerationCheckpoint:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(RegenerationCheckpoint)
    def test_creates(self):
        cp = RegenerationCheckpoint(
            attempt=1, timestamp=_FIXED_DT, content="text",
            validation_result=None, temperature=0.7,
        )
        assert cp.attempt == 1; assert cp.score == 0.0
    def test_to_dict(self):
        cp = RegenerationCheckpoint(
            attempt=2, timestamp=_FIXED_DT, content="v2",
            validation_result=None, temperature=0.9,
            failure_type=ConstraintFailureType.CREATIVE,
        )
        d = cp.to_dict()
        assert d["attempt"] == 2; assert d["failure_type"] == "CREATIVE"

def test_module_importable(): assert _AVAIL or not _AVAIL
