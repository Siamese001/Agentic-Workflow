"""GAP-C: Step 8 window aggregation correctness — counts summed across N records; determinism."""

import pytest

from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
from system_learning.engines.in_memory_healing_outcome_intake_store import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    InMemoryHealingOutcomeIntakeStore,
)
from system_learning.types.healing_outcome_types import HealingOutcomeEvent


def _build_adapter_with_records(records_spec):
    """records_spec: list of (created_utc, healer_id, success_count, failure_count)"""
    store = InMemoryHealingOutcomeIntakeStore()
    adapter = HealingOutcomeIntakeAdapter(store=store)
    for created_utc, healer_id, success_count, failure_count in records_spec:
        agg = HealingOutcomeAggregator(window_size=success_count + failure_count + 1)
        for _ in range(success_count):
            agg.ingest(
                HealingOutcomeEvent(
                    healer_id=healer_id,
                    tier="L0",
                    failure_type="F",
                    success=True,
                    timestamp_utc=created_utc,
                )
            )
        for _ in range(failure_count):
            agg.ingest(
                HealingOutcomeEvent(
                    healer_id=healer_id,
                    tier="L0",
                    failure_type="F",
                    success=False,
                    timestamp_utc=created_utc,
                )
            )
        rec = adapter.build_record(aggregator=agg, created_utc=created_utc, source="test")
        adapter.persist_record(rec)
    return adapter


def _reconstruct_window_aggregator(adapter, window_start, window_end, now_utc):
    """Replicates the Step 8 window aggregation logic for test assertions."""
    window_records = adapter.get_recent_records(window_start, window_end)
    if not window_records:
        return None
    wa = HealingOutcomeAggregator(window_size=10000)
    for rec in window_records:
        for s in rec.snapshot:
            for _ in range(s.success_count):
                wa.ingest(
                    HealingOutcomeEvent(
                        healer_id=s.healer_id,
                        tier=s.tier,
                        failure_type=s.failure_type,
                        success=True,
                        timestamp_utc=now_utc,
                    )
                )
            for _ in range(s.failure_count):
                wa.ingest(
                    HealingOutcomeEvent(
                        healer_id=s.healer_id,
                        tier=s.tier,
                        failure_type=s.failure_type,
                        success=False,
                        timestamp_utc=now_utc,
                    )
                )
    return wa


@pytest.mark.unit_min_deps
class TestStep8WindowAggregation:
    def test_window_aggregate_sums_counts_across_records(self):
        """Total ingested events across N records must equal sum of individual counts."""
        specs = [
            (1_000_000, "agent_a", 3, 1),
            (1_000_100, "agent_a", 2, 0),
            (1_000_200, "agent_b", 0, 4),
        ]
        adapter = _build_adapter_with_records(specs)
        now_utc = 1_000_300

        wa = _reconstruct_window_aggregator(adapter, 999_999, 1_000_300, now_utc)
        assert wa is not None

        snapshot = list(wa.snapshot())
        # Total successes: 3+2+0=5, total failures: 1+0+4=5
        total_success = sum(s.success_count for s in snapshot)
        total_failure = sum(s.failure_count for s in snapshot)
        assert total_success == 5
        assert total_failure == 5

    def test_window_excludes_records_outside_range(self):
        """Records outside window bounds must not be included in aggregation."""
        specs = [
            (500_000, "agent_x", 10, 0),  # outside window
            (1_000_000, "agent_y", 2, 1),  # inside window
        ]
        adapter = _build_adapter_with_records(specs)

        records_in = adapter.get_recent_records(900_000, 1_100_000)
        assert len(records_in) == 1
        assert records_in[0].created_utc == 1_000_000

    def test_determinism_same_records_same_snapshot_bytes(self):
        """Same window records → identical canonical_bytes() on the built intake record."""
        specs = [
            (1_000_000, "agent_det", 4, 2),
            (1_000_050, "agent_det", 1, 3),
        ]
        now_utc = 1_000_100

        def build_intake_bytes():
            adapter = _build_adapter_with_records(specs)
            wa = _reconstruct_window_aggregator(adapter, 999_999, 1_000_100, now_utc)
            store2 = InMemoryHealingOutcomeIntakeStore()
            adapter2 = HealingOutcomeIntakeAdapter(store=store2)
            rec = adapter2.build_record(aggregator=wa, created_utc=now_utc, source="det-test")
            return rec.canonical_bytes()

        assert build_intake_bytes() == build_intake_bytes()

    def test_empty_window_returns_none_aggregator(self):
        """get_recent_records on empty window → no aggregator built."""
        adapter = _build_adapter_with_records([])
        wa = _reconstruct_window_aggregator(adapter, 0, 9_999_999, 1_000_000)
        assert wa is None

    def test_single_record_window_correct_counts(self):
        """Single record in window: aggregator snapshot matches exactly the record counts."""
        specs = [(2_000_000, "solo_agent", 7, 3)]
        adapter = _build_adapter_with_records(specs)
        wa = _reconstruct_window_aggregator(adapter, 1_999_999, 2_000_001, 2_000_100)
        assert wa is not None
        snapshot = list(wa.snapshot())
        total_success = sum(s.success_count for s in snapshot)
        total_failure = sum(s.failure_count for s in snapshot)
        assert total_success == 7
        assert total_failure == 3

    def test_reordered_records_same_aggregate(self):
        """Metamorphic: ingesting snapshot counts in any order yields same totals."""
        # Two records with different healers
        specs_forward = [
            (1_000_000, "agent_m1", 5, 2),
            (1_000_100, "agent_m2", 3, 1),
        ]
        specs_reverse = [
            (1_000_000, "agent_m2", 3, 1),
            (1_000_100, "agent_m1", 5, 2),
        ]
        now_utc = 1_000_200

        adapter_fwd = _build_adapter_with_records(specs_forward)
        adapter_rev = _build_adapter_with_records(specs_reverse)

        wa_fwd = _reconstruct_window_aggregator(adapter_fwd, 999_999, 1_000_200, now_utc)
        wa_rev = _reconstruct_window_aggregator(adapter_rev, 999_999, 1_000_200, now_utc)

        snap_fwd = list(wa_fwd.snapshot())
        snap_rev = list(wa_rev.snapshot())

        total_s_fwd = sum(s.success_count for s in snap_fwd)
        total_f_fwd = sum(s.failure_count for s in snap_fwd)
        total_s_rev = sum(s.success_count for s in snap_rev)
        total_f_rev = sum(s.failure_count for s in snap_rev)

        assert total_s_fwd == total_s_rev
        assert total_f_fwd == total_f_rev
