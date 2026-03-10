"""
Phase 3 — Wave 2 Tests: L4 persistence + no-same-cycle enforcement.
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.types.detection_signal_store_types import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    DetectionSignalStore,
)
from agentic_core.L6_observability.types.detection_signal_types import DetectionSignal

pytestmark = pytest.mark.unit_min_deps


def _sig(mission_id: str, created_at_utc: int, anomaly_score: float = 0.3) -> DetectionSignal:
    return DetectionSignal.build(
        mission_id=mission_id,
        created_at_utc=created_at_utc,
        anomaly_score=anomaly_score,
        escalation_rate=0.0,
        retry_rate=0.0,
        violation_density=0.0,
    )


class TestDetectionSignalStore:
    def _fresh(self) -> DetectionSignalStore:
        return DetectionSignalStore()

    def test_store_returns_signal_hash(self):
        store = self._fresh()
        sig = _sig("m-001", 100)
        returned_hash = store.store(sig, commit_tick=1)
        assert returned_hash == sig.signal_hash

    def test_store_and_fetch_latest_prior_only(self):
        """
        Store signal at tick 5; fetch with before_tick=10 must return it.
        """
        store = self._fresh()
        sig = _sig("m-prior", 100, anomaly_score=0.5)
        store.store(sig, commit_tick=5)
        result = store.fetch_latest(before_tick=10)
        assert result is not None
        assert result.signal_hash == sig.signal_hash

    def test_fetch_latest_disallows_same_cycle_signal(self):
        """
        Negative: store signal at tick T; fetch with before_tick=T must return None.
        Same-cycle signal is invisible.
        """
        store = self._fresh()
        sig = _sig("m-same-cycle", 100, anomaly_score=0.9)
        store.store(sig, commit_tick=10)
        result = store.fetch_latest(before_tick=10)
        assert result is None, "Same-cycle signal must not be returned by fetch_latest(before_tick=T)"

    def test_fetch_latest_returns_none_when_empty(self):
        store = self._fresh()
        assert store.fetch_latest(before_tick=100) is None

    def test_fetch_latest_returns_most_recent_prior(self):
        """With multiple signals, fetch returns the most recent one before boundary."""
        store = self._fresh()
        sig1 = _sig("m-a", 100, anomaly_score=0.1)
        sig2 = _sig("m-b", 200, anomaly_score=0.8)
        store.store(sig1, commit_tick=1)
        store.store(sig2, commit_tick=2)
        result = store.fetch_latest(before_tick=3)
        assert result is not None
        assert result.signal_hash == sig2.signal_hash

    def test_fetch_latest_excludes_signals_at_or_after_boundary(self):
        store = self._fresh()
        sig1 = _sig("m-old", 100, anomaly_score=0.2)
        sig2 = _sig("m-new", 200, anomaly_score=0.9)
        store.store(sig1, commit_tick=5)
        store.store(sig2, commit_tick=10)
        result = store.fetch_latest(before_tick=10)
        assert result is not None
        assert result.signal_hash == sig1.signal_hash

    def test_monotonicity_enforced(self):
        """Storing at a non-increasing tick must raise ValueError."""
        store = self._fresh()
        sig1 = _sig("m-mono-1", 100)
        sig2 = _sig("m-mono-2", 200)
        store.store(sig1, commit_tick=5)
        with pytest.raises(ValueError, match="strictly greater"):
            store.store(sig2, commit_tick=5)

    def test_storage_uses_canonical_bytes_and_hash(self):
        """Verify stored signal_hash matches independently computed hash."""
        store = self._fresh()
        sig = _sig("m-hash-check", 300, anomaly_score=0.4)
        expected_hash = DetectionSignal.compute_hash(
            schema_version=sig.schema_version,
            mission_id=sig.mission_id,
            created_at_utc=sig.created_at_utc,
            anomaly_score=sig.anomaly_score,
            escalation_rate=sig.escalation_rate,
            retry_rate=sig.retry_rate,
            violation_density=sig.violation_density,
        )
        store.store(sig, commit_tick=1)
        fetched = store.fetch_latest(before_tick=2)
        assert fetched is not None
        assert fetched.signal_hash == expected_hash

    def test_count_tracks_stored_signals(self):
        store = self._fresh()
        assert store.count() == 0
        store.store(_sig("m-c1", 100), commit_tick=1)
        assert store.count() == 1
        store.store(_sig("m-c2", 200), commit_tick=2)
        assert store.count() == 2


class TestGetPriorDetectionSignal:
    """Tests for the get_prior_detection_signal helper (prior-only semantics)."""

    def test_get_prior_returns_none_when_no_prior_exists(self):
        """Fresh store: no prior signal for any tick."""
        store = DetectionSignalStore()
        result = store.fetch_latest(before_tick=1)
        assert result is None

    def test_get_prior_strictly_excludes_same_tick(self):
        """
        Negative: signal stored at tick T must not be returned when
        execution_start_tick == T.
        """
        store = DetectionSignalStore()
        sig = _sig("m-excl", 500, anomaly_score=0.95)
        store.store(sig, commit_tick=7)
        result = store.fetch_latest(before_tick=7)
        assert result is None

    def test_get_prior_returns_signal_from_previous_tick(self):
        store = DetectionSignalStore()
        sig = _sig("m-prev", 400, anomaly_score=0.6)
        store.store(sig, commit_tick=3)
        result = store.fetch_latest(before_tick=4)
        assert result is not None
        assert result.signal_hash == sig.signal_hash
