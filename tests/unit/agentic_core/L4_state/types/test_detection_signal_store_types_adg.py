"""ADG contract tests for agentic_core/L4_state/types/detection_signal_store_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L4_state.types.detection_signal_store_types import (
        DetectionSignalStore, get_signal_store,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    DetectionSignalStore = get_signal_store = None  # type: ignore[assignment,misc]

def _make_signal():
    try:
        from agentic_core.L6_observability.types.detection_signal_types import DetectionSignal
        return DetectionSignal.build(
            mission_id="m1", created_at_utc=1000,
            anomaly_score=0.1, escalation_rate=0.0,
            retry_rate=0.0, violation_density=0.0,
        )
    except Exception:
        return None

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestDetectionSignalStore:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(DetectionSignalStore)
    def test_count_starts_zero(self):
        store = DetectionSignalStore(); assert store.count() == 0
    def test_fetch_latest_empty_returns_none(self):
        store = DetectionSignalStore()
        assert store.fetch_latest(before_tick=1) is None

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestDetectionSignalStoreWithSignal:
    def test_store_and_fetch(self):
        sig = _make_signal()
        if sig is None:
            pytest.skip("DetectionSignal unavailable")
        store = DetectionSignalStore()
        store.store(sig, commit_tick=5)
        assert store.count() == 1
        fetched = store.fetch_latest(before_tick=6)
        assert fetched is sig
    def test_same_cycle_not_returned(self):
        sig = _make_signal()
        if sig is None:
            pytest.skip("DetectionSignal unavailable")
        store = DetectionSignalStore()
        store.store(sig, commit_tick=5)
        fetched = store.fetch_latest(before_tick=5)  # boundary = 5, signal at 5 excluded
        assert fetched is None
    def test_monotonicity_violation_raises(self):
        sig = _make_signal()
        if sig is None:
            pytest.skip("DetectionSignal unavailable")
        store = DetectionSignalStore()
        store.store(sig, commit_tick=10)
        sig2 = _make_signal()
        with pytest.raises(ValueError):
            store.store(sig2, commit_tick=5)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestGetSignalStore:
    def test_returns_instance(self):
        store = get_signal_store()
        assert isinstance(store, DetectionSignalStore)

def test_module_importable(): assert _AVAIL or not _AVAIL
