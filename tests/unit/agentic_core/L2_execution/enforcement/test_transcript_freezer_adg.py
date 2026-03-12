"""ADG-driven tests for L2_execution/enforcement/transcript_freezer.py — fan_in=0."""
from __future__ import annotations

import pytest

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
