"""ADG-driven tests for L2_execution/enforcement/transcript_freezer.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_transcript_freezer_adg")
_emit_applies_guardrail("p0", "test_transcript_freezer_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_transcript_freezer_adg", "policy_binding")
_emit_snapshots_state("p0", "test_transcript_freezer_adg", "state_snapshot")
emit_replay_key("p0", "test_transcript_freezer_adg")
emit_determinism_digest("p0", "test_transcript_freezer_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.enforcement.transcript_freezer import (
    FrozenTranscript,
    TranscriptMutationViolation,
    freeze_transcript,
)


class TestTranscriptMutationViolation:
    def test_is_exception(self):
        assert issubclass(TranscriptMutationViolation, Exception)


class TestFrozenTranscript:
    def test_creates(self):
        ft = FrozenTranscript(["step1", "step2"])
        assert len(ft) == 2

    def test_getitem(self):
        ft = FrozenTranscript(["a", "b", "c"])
        assert ft[0] == "a"
        assert ft[2] == "c"

    def test_append_raises(self):
        ft = FrozenTranscript(["step1"])
        with pytest.raises(TranscriptMutationViolation):
            ft.append("step2")

    def test_setitem_raises(self):
        ft = FrozenTranscript(["step1"])
        with pytest.raises(TranscriptMutationViolation):
            ft[0] = "changed"

    def test_insert_raises(self):
        ft = FrozenTranscript(["step1"])
        with pytest.raises(TranscriptMutationViolation):
            ft.insert(0, "new")


class TestFreezeTranscript:
    def test_callable(self):
        assert callable(freeze_transcript)

    def test_returns_frozen_transcript(self):
        ft = freeze_transcript(["a", "b"])
        assert isinstance(ft, FrozenTranscript)
        assert len(ft) == 2
