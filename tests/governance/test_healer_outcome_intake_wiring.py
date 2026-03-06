"""
Integration tests for L2 healer → system_learning outcome intake wiring (G17).

Verifies:
- HealingOutcomeAggregator → HealingOutcomeIntakeAdapter → InMemory store pipeline
- build_record produces deterministically sorted snapshots
- persist_record writes to store
- empty aggregator raises (snapshot cannot be empty)
- duplicate persist is additive (store grows)
- schema_version, window_size, source all correct
- determinism: identical aggregator state → identical record
"""

from __future__ import annotations

import pytest

from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
from system_learning.ports.healing_outcome_intake_store import HealingOutcomeIntakeStore
from system_learning.types.healing_outcome_types import HealingOutcomeEvent


# ---------------------------------------------------------------------------
# In-memory store for testing (implements write() protocol)
# ---------------------------------------------------------------------------

class InMemoryHealingOutcomeIntakeStore(HealingOutcomeIntakeStore):
    """Simple in-memory store for tests."""

    def __init__(self):
        self._records = []

    def write(self, record):
        self._records.append(record)

    def read_all(self):
        return list(self._records)

    def count(self):
        return len(self._records)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_event(healer_id="healer_1", tier="T1", failure_type="OOM", success=True):
    return HealingOutcomeEvent(
        healer_id=healer_id,
        tier=tier,
        failure_type=failure_type,
        success=success,
        timestamp_utc=1234567890,
        trace_id="trace_001",
    )


def _populated_aggregator():
    agg = HealingOutcomeAggregator()
    agg.ingest(_make_event("healer_b", "T2", "IMPORT_ERROR", success=True))
    agg.ingest(_make_event("healer_a", "T1", "OOM", success=True))
    agg.ingest(_make_event("healer_a", "T1", "OOM", success=False))
    return agg


# ---------------------------------------------------------------------------
# TestAdapterBuildRecord
# ---------------------------------------------------------------------------

class TestAdapterBuildRecord:
    def test_build_record_returns_intake_record(self):
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        agg = _populated_aggregator()
        record = adapter.build_record(agg, created_utc=1000)
        from system_learning.types.healing_outcome_intake_types import HealingOutcomeIntakeRecord
        assert isinstance(record, HealingOutcomeIntakeRecord)

    def test_build_record_schema_version_is_1(self):
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        agg = _populated_aggregator()
        record = adapter.build_record(agg, created_utc=1000)
        assert record.schema_version == 1

    def test_build_record_window_size_matches_snapshot_length(self):
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        agg = _populated_aggregator()
        record = adapter.build_record(agg, created_utc=1000)
        assert record.window_size == len(record.snapshot)

    def test_build_record_created_utc_matches_argument(self):
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        agg = _populated_aggregator()
        record = adapter.build_record(agg, created_utc=9999999)
        assert record.created_utc == 9999999

    def test_build_record_default_source(self):
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        agg = _populated_aggregator()
        record = adapter.build_record(agg, created_utc=1000)
        assert record.source == "L2.3-healing"

    def test_build_record_custom_source(self):
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        agg = _populated_aggregator()
        record = adapter.build_record(agg, created_utc=1000, source="test-source")
        assert record.source == "test-source"

    def test_build_record_snapshot_is_deterministically_sorted(self):
        """Snapshot entries must be sorted by (healer_id, tier, failure_type)."""
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        agg = _populated_aggregator()
        record = adapter.build_record(agg, created_utc=1000)
        snap = record.snapshot
        sorted_snap = tuple(
            sorted(snap, key=lambda s: (s.healer_id, s.tier, s.failure_type))
        )
        assert snap == sorted_snap

    def test_build_record_deterministic_for_identical_aggregator(self):
        """Same aggregator state → same record content (no wall-clock)."""
        store1 = InMemoryHealingOutcomeIntakeStore()
        store2 = InMemoryHealingOutcomeIntakeStore()
        adapter1 = HealingOutcomeIntakeAdapter(store1)
        adapter2 = HealingOutcomeIntakeAdapter(store2)

        agg1 = _populated_aggregator()
        agg2 = _populated_aggregator()

        r1 = adapter1.build_record(agg1, created_utc=5000)
        r2 = adapter2.build_record(agg2, created_utc=5000)

        assert r1.window_size == r2.window_size
        assert r1.snapshot == r2.snapshot
        assert r1.schema_version == r2.schema_version


# ---------------------------------------------------------------------------
# TestAdapterPersistRecord
# ---------------------------------------------------------------------------

class TestAdapterPersistRecord:
    def test_persist_record_writes_to_store(self):
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        agg = _populated_aggregator()
        record = adapter.build_record(agg, created_utc=1000)
        adapter.persist_record(record)
        assert store.count() == 1

    def test_persist_record_multiple_writes_additive(self):
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        agg = _populated_aggregator()
        for i in range(3):
            record = adapter.build_record(agg, created_utc=1000 + i)
            adapter.persist_record(record)
        assert store.count() == 3

    def test_persisted_record_retrievable(self):
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        agg = _populated_aggregator()
        record = adapter.build_record(agg, created_utc=42)
        adapter.persist_record(record)
        retrieved = store.read_all()[0]
        assert retrieved.created_utc == 42
        assert retrieved.schema_version == 1

    def test_store_write_called_once_per_persist(self):
        from unittest.mock import MagicMock
        store_mock = MagicMock(spec=HealingOutcomeIntakeStore)
        adapter = HealingOutcomeIntakeAdapter(store_mock)
        agg = _populated_aggregator()
        record = adapter.build_record(agg, created_utc=1)
        adapter.persist_record(record)
        store_mock.write.assert_called_once_with(record)


# ---------------------------------------------------------------------------
# TestEmptyAggregatorRejection
# ---------------------------------------------------------------------------

class TestEmptyAggregatorRejection:
    def test_empty_aggregator_build_record_raises_value_error(self):
        """Empty aggregator has window_size=0 after snapshot, which is invalid."""
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        empty_agg = HealingOutcomeAggregator()
        # Empty snapshot → window_size=0 → HealingOutcomeIntakeRecord.__post_init__ raises
        with pytest.raises(ValueError):
            adapter.build_record(empty_agg, created_utc=0)


# ---------------------------------------------------------------------------
# TestFullPipeline
# ---------------------------------------------------------------------------

class TestFullPipeline:
    def test_full_pipeline_healer_to_store(self):
        """End-to-end: ingest events → aggregate → build record → persist."""
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)

        agg = HealingOutcomeAggregator()
        # Ingest 5 events for two healers
        for _ in range(3):
            agg.ingest(_make_event("healer_x", "T1", "TIMEOUT", success=True))
        for _ in range(2):
            agg.ingest(_make_event("healer_x", "T1", "TIMEOUT", success=False))
        agg.ingest(_make_event("healer_y", "T3", "OOM", success=True))

        record = adapter.build_record(agg, created_utc=2000, source="test-pipeline")
        adapter.persist_record(record)

        assert store.count() == 1
        r = store.read_all()[0]
        assert r.source == "test-pipeline"
        assert r.window_size >= 1
        # healer_x stats should show 3 successes, 2 failures
        healer_x_stats = [s for s in r.snapshot if s.healer_id == "healer_x"]
        assert len(healer_x_stats) == 1
        assert healer_x_stats[0].success_count == 3
        assert healer_x_stats[0].failure_count == 2
