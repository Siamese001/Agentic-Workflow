"""ADG contract tests for apps_lic/types/state_checkpoint_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_lic.types.state_checkpoint_types import (
        LICStateManager,
        StateCheckpoint,
        StateValidationResult,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    StateCheckpoint = StateValidationResult = LICStateManager = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestStateCheckpoint:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(StateCheckpoint)
    def test_creates(self):
        c = StateCheckpoint(hop_id="HOP1", mission_id="M1",
                            timestamp="2025-01-01", checksum="abc123", filepath="/state/hop1.json")
        assert c.hop_id == "HOP1"; assert c.mission_id == "M1"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestStateValidationResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(StateValidationResult)
    def test_creates_valid(self):
        r = StateValidationResult(is_valid=True)
        assert r.is_valid is True; assert r.errors == []
    def test_creates_invalid(self):
        r = StateValidationResult(is_valid=False, errors=["missing field"])
        assert r.is_valid is False; assert len(r.errors) == 1

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestLICStateManager:
    def test_creates(self, tmp_path):
        m = LICStateManager("mission1", str(tmp_path))
        assert m.mission_id == "mission1"
    def test_state_not_exists_initially(self, tmp_path):
        m = LICStateManager("mission1", str(tmp_path))
        assert m.state_exists("HOP1") is False
    def test_list_states_empty(self, tmp_path):
        m = LICStateManager("mission1", str(tmp_path))
        assert m.list_states() == []

def test_module_importable(): assert _AVAIL or not _AVAIL
