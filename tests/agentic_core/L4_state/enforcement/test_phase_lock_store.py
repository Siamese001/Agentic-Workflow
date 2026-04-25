"""Tests for PhaseLockStore - phase lock state management."""
import pytest
from agentic_core.L4_state.enforcement.phase_lock_store import PhaseLockStore


class TestPhaseLockStore:
    def test_init(self, tmp_path):
        store = PhaseLockStore(path=str(tmp_path / "phase.json"))
        assert store is not None

    def test_acquire_lock(self, tmp_path):
        store = PhaseLockStore(path=str(tmp_path / "phase.json"))
        result = store.acquire(phase="W1", owner="agent1")
        assert result is True

    def test_acquire_lock_held(self, tmp_path):
        store = PhaseLockStore(path=str(tmp_path / "phase.json"))
        store.acquire(phase="W1", owner="agent1")
        result = store.acquire(phase="W1", owner="agent2")
        assert result is False

    def test_release_lock(self, tmp_path):
        store = PhaseLockStore(path=str(tmp_path / "phase.json"))
        store.acquire(phase="W1", owner="agent1")
        store.release(phase="W1", owner="agent1")
        # Now another can acquire
        assert store.acquire(phase="W1", owner="agent2") is True

    def test_release_wrong_owner(self, tmp_path):
        store = PhaseLockStore(path=str(tmp_path / "phase.json"))
        store.acquire(phase="W1", owner="agent1")
        with pytest.raises(PermissionError):
            store.release(phase="W1", owner="agent2")

    def test_get_lock_status(self, tmp_path):
        store = PhaseLockStore(path=str(tmp_path / "phase.json"))
        store.acquire(phase="W1", owner="agent1")
        status = store.get_status("W1")
        assert status["owner"] == "agent1"

    def test_persistence(self, tmp_path):
        path = str(tmp_path / "phase.json")
        store1 = PhaseLockStore(path=path)
        store1.acquire(phase="W1", owner="agent1")
        store2 = PhaseLockStore(path=path)
        status = store2.get_status("W1")
        assert status["owner"] == "agent1"
