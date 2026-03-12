"""ADG contract tests for L4_state/types/state_checkpoint_types.py."""
from __future__ import annotations
import pytest
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
