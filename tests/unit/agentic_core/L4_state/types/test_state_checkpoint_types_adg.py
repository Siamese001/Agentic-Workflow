"""ADG contract tests for L4_state/types/state_checkpoint_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_state_checkpoint_types_adg")
_emit_applies_guardrail("p0", "test_state_checkpoint_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_state_checkpoint_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_state_checkpoint_types_adg", "state_snapshot")
emit_replay_key("p0", "test_state_checkpoint_types_adg")
emit_determinism_digest("p0", "test_state_checkpoint_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
pytestmark = pytest.mark.unit
from agentic_core.L4_state.types.state_checkpoint_types import StateCheckpoint, StateValidationResult


class TestStateCheckpoint:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(StateCheckpoint)
    def test_creates(self):
        s = StateCheckpoint(_hop_id="h1", _mission_id="m1", _timestamp="2026-01-01",
                            _checksum="abc", _filepath="/tmp/x.json")
        assert s._hop_id == "h1"

class TestStateValidationResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(StateValidationResult)
    def test_creates_valid(self):
        r = StateValidationResult(_is_valid=True)
        assert r._is_valid is True; assert r._errors == []
    def test_invalid_with_errors(self):
        r = StateValidationResult(_is_valid=False, _errors=["missing field"])
        assert r._is_valid is False; assert len(r._errors) == 1
