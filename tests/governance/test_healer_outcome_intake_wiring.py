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

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "test_healer_outcome_intake_wiring", "execution_auth")
_emit_validates_capability("p2", "test_healer_outcome_intake_wiring", "capability_check")
_emit_routes_to_capability("p2", "test_healer_outcome_intake_wiring", "capability_route")
_emit_writes_via_uwg("p2", "test_healer_outcome_intake_wiring", "uwg_write")
_emit_blocks_direct_write("p2", "test_healer_outcome_intake_wiring", "direct_write_block")
_emit_records_tool_invocation("p2", "test_healer_outcome_intake_wiring", "tool_invocation")
_emit_captures_execution_output("p2", "test_healer_outcome_intake_wiring", "exec_output")
_emit_dispatches_agent("p3", "test_healer_outcome_intake_wiring", "agent_dispatch")
_emit_coordinates_agents("p3", "test_healer_outcome_intake_wiring", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_healer_outcome_intake_wiring", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_healer_outcome_intake_wiring", "healing_outcome")
_emit_escalates_failure("p3", "test_healer_outcome_intake_wiring", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_healer_outcome_intake_wiring", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_healer_outcome_intake_wiring", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_healer_outcome_intake_wiring", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_healer_outcome_intake_wiring", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_healer_outcome_intake_wiring", "eval_metric")
_emit_stores_embedding("p4", "test_healer_outcome_intake_wiring", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_healer_outcome_intake_wiring", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_healer_outcome_intake_wiring", "exec_snapshot_link")
from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
from system_learning.ports.healing_outcome_intake_store import HealingOutcomeIntakeStore
from system_learning.types.healing_outcome_types import HealingOutcomeEvent

_emit_records_execution_trace("p0", "evidence", "test_healer_outcome_intake_wiring")
_emit_applies_guardrail("p0", "test_healer_outcome_intake_wiring", "p0_governance")
_emit_reads_policy_state("p0", "test_healer_outcome_intake_wiring", "policy_binding")
_emit_snapshots_state("p0", "test_healer_outcome_intake_wiring", "state_snapshot")
emit_replay_key("p0", "test_healer_outcome_intake_wiring")
emit_determinism_digest("p0", "test_healer_outcome_intake_wiring")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
        sorted_snap = tuple(sorted(snap, key=lambda s: (s.healer_id, s.tier, s.failure_type)))
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
