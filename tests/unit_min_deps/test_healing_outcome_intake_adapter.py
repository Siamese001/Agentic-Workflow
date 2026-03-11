"""Tests for HealingOutcomeIntakeAdapter."""

import pytest

from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
from system_learning.engines.in_memory_healing_outcome_intake_store import InMemoryHealingOutcomeIntakeStore
from system_learning.types.healing_outcome_types import HealingOutcomeEvent


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@pytest.mark.unit_min_deps
class TestHealingOutcomeIntakeAdapter:
    """Test suite for HealingOutcomeIntakeAdapter."""

    def test_build_record_determinism(self) -> None:
        """Test that identical inputs produce identical records."""
        # Setup
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)

        # Create two aggregators with identical events
        event1 = HealingOutcomeEvent(
            healer_id="healer1", tier="LOCAL_AGENT", failure_type="timeout", success=False, timestamp_utc=1000
        )
        event2 = HealingOutcomeEvent(
            healer_id="healer2", tier="QWEN_VLLM", failure_type="exception", success=True, timestamp_utc=2000
        )

        # Build first record
        aggregator1 = HealingOutcomeAggregator(window_size=10)
        aggregator1.ingest(event1)
        aggregator1.ingest(event2)
        record1 = adapter.build_record(aggregator1, created_utc=3000, source="test")

        # Build second record with same inputs
        aggregator2 = HealingOutcomeAggregator(window_size=10)
        aggregator2.ingest(event1)
        aggregator2.ingest(event2)
        record2 = adapter.build_record(aggregator2, created_utc=3000, source="test")

        # Assert records are identical
        assert record1 == record2
        assert record1.schema_version == 1
        assert record1.created_utc == 3000
        assert record1.window_size == 2
        assert record1.source == "test"

        # Verify snapshot is sorted deterministically
        snapshot = record1.snapshot
        assert len(snapshot) == 2
        # Should be sorted by (healer_id, tier, failure_type)
        assert snapshot[0].healer_id == "healer1"
        assert snapshot[1].healer_id == "healer2"

    def test_persist_record_calls_store_exactly_once(self) -> None:
        """Test that persist_record calls store.write exactly once."""
        # Setup
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)

        # Create a record
        aggregator = HealingOutcomeAggregator(window_size=10)
        event = HealingOutcomeEvent(
            healer_id="healer1", tier="LOCAL_AGENT", failure_type="timeout", success=False, timestamp_utc=1000
        )
        aggregator.ingest(event)
        record = adapter.build_record(aggregator, created_utc=2000, source="test")

        # Persist record
        adapter.persist_record(record)

        # Verify store was called exactly once
        assert store.count() == 1
        stored_records = store.get_records()
        assert len(stored_records) == 1
        assert stored_records[0] == record

    def test_empty_aggregator_raises_error(self) -> None:
        """Test that building record from empty aggregator raises error."""
        # Setup
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        empty_aggregator = HealingOutcomeAggregator(window_size=10)

        # Should raise ValueError for empty snapshot (window_size validation happens first)
        with pytest.raises(ValueError, match="window_size must be positive"):
            adapter.build_record(empty_aggregator, created_utc=1000, source="test")

    def test_snapshot_sorting_enforced(self) -> None:
        """Test that snapshot is always sorted deterministically."""
        # Setup
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)

        # Create events in non-sorted order
        events = [
            HealingOutcomeEvent(
                healer_id="zebra", tier="GEMINI_2_5_PRO", failure_type="z", success=False, timestamp_utc=3000
            ),
            HealingOutcomeEvent(
                healer_id="alpha", tier="LOCAL_AGENT", failure_type="a", success=True, timestamp_utc=1000
            ),
            HealingOutcomeEvent(
                healer_id="beta", tier="QWEN_VLLM", failure_type="b", success=False, timestamp_utc=2000
            ),
        ]

        # Ingest in non-sorted order
        aggregator = HealingOutcomeAggregator(window_size=10)
        for event in events:
            aggregator.ingest(event)

        # Build record
        record = adapter.build_record(aggregator, created_utc=4000, source="test")

        # Verify snapshot is sorted by (healer_id, tier, failure_type)
        snapshot = record.snapshot
        assert len(snapshot) == 3

        # Check sorting order
        assert snapshot[0].healer_id == "alpha"
        assert snapshot[1].healer_id == "beta"
        assert snapshot[2].healer_id == "zebra"

        # Verify tuple is immutable
        with pytest.raises(AttributeError):
            snapshot[0].healer_id = "changed"
