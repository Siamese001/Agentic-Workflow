"""GAP-C/E: HealingOutcomeIntakeAdapter.get_recent_records() interface contract."""

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

_emit_authorize_and_execute("p2", "test_adapter_get_recent_records", "execution_auth")
_emit_validates_capability("p2", "test_adapter_get_recent_records", "capability_check")
_emit_routes_to_capability("p2", "test_adapter_get_recent_records", "capability_route")
_emit_writes_via_uwg("p2", "test_adapter_get_recent_records", "uwg_write")
_emit_blocks_direct_write("p2", "test_adapter_get_recent_records", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adapter_get_recent_records", "tool_invocation")
_emit_captures_execution_output("p2", "test_adapter_get_recent_records", "exec_output")
_emit_dispatches_agent("p3", "test_adapter_get_recent_records", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adapter_get_recent_records", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adapter_get_recent_records", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adapter_get_recent_records", "healing_outcome")
_emit_escalates_failure("p3", "test_adapter_get_recent_records", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adapter_get_recent_records", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adapter_get_recent_records", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adapter_get_recent_records", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adapter_get_recent_records", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adapter_get_recent_records", "eval_metric")
_emit_stores_embedding("p4", "test_adapter_get_recent_records", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adapter_get_recent_records", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adapter_get_recent_records", "exec_snapshot_link")
from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
from system_learning.engines.in_memory_healing_outcome_intake_store import (
    InMemoryHealingOutcomeIntakeStore,
)
from system_learning.types.healing_outcome_types import HealingOutcomeEvent

_emit_records_execution_trace("p0", "evidence", "test_adapter_get_recent_records")
_emit_applies_guardrail("p0", "test_adapter_get_recent_records", "p0_governance")
_emit_reads_policy_state("p0", "test_adapter_get_recent_records", "policy_binding")
_emit_snapshots_state("p0", "test_adapter_get_recent_records", "state_snapshot")
emit_replay_key("p0", "test_adapter_get_recent_records")
emit_determinism_digest("p0", "test_adapter_get_recent_records")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


def _make_adapter():
    store = InMemoryHealingOutcomeIntakeStore()
    return HealingOutcomeIntakeAdapter(store=store)


def _persist_record(adapter, created_utc, healer_id="agent_x", success=True):
    agg = HealingOutcomeAggregator(window_size=1)
    agg.ingest(
        HealingOutcomeEvent(
            healer_id=healer_id,
            tier="L0",
            failure_type="F",
            success=success,
            timestamp_utc=created_utc,
        )
    )
    rec = adapter.build_record(aggregator=agg, created_utc=created_utc, source="test")
    adapter.persist_record(rec)
    return rec


@pytest.mark.unit_min_deps
class TestAdapterGetRecentRecords:
    def test_get_recent_records_method_exists(self):
        """HealingOutcomeIntakeAdapter must expose get_recent_records()."""
        adapter = _make_adapter()
        assert hasattr(adapter, "get_recent_records"), (
            "get_recent_records method missing from HealingOutcomeIntakeAdapter"
        )
        assert callable(adapter.get_recent_records)

    def test_get_records_on_protocol(self):
        """HealingOutcomeIntakeStore protocol must declare get_records()."""
        from system_learning.ports.healing_outcome_intake_store import HealingOutcomeIntakeStore

        assert hasattr(HealingOutcomeIntakeStore, "get_records"), (
            "get_records() not declared on HealingOutcomeIntakeStore protocol"
        )

    def test_empty_store_returns_empty_list(self):
        """Empty store → get_recent_records returns []."""
        adapter = _make_adapter()
        assert adapter.get_recent_records(0, 9_999_999) == []

    def test_record_in_window_is_returned(self):
        """A record with created_utc inside [start, end] is returned."""
        adapter = _make_adapter()
        rec = _persist_record(adapter, created_utc=5_000_000)
        results = adapter.get_recent_records(4_999_999, 5_000_001)
        assert len(results) == 1
        assert results[0].created_utc == 5_000_000

    def test_record_before_window_excluded(self):
        """Record before window_start_utc must be excluded."""
        adapter = _make_adapter()
        _persist_record(adapter, created_utc=1_000)
        results = adapter.get_recent_records(window_start_utc=2_000, window_end_utc=9_999)
        assert len(results) == 0

    def test_record_after_window_excluded(self):
        """Record after window_end_utc must be excluded."""
        adapter = _make_adapter()
        _persist_record(adapter, created_utc=9_999_999)
        results = adapter.get_recent_records(window_start_utc=0, window_end_utc=9_999_998)
        assert len(results) == 0

    def test_exact_boundary_start_included(self):
        """Record at exactly window_start_utc must be included."""
        adapter = _make_adapter()
        _persist_record(adapter, created_utc=1_000_000)
        results = adapter.get_recent_records(1_000_000, 2_000_000)
        assert len(results) == 1

    def test_exact_boundary_end_included(self):
        """Record at exactly window_end_utc must be included."""
        adapter = _make_adapter()
        _persist_record(adapter, created_utc=2_000_000)
        results = adapter.get_recent_records(1_000_000, 2_000_000)
        assert len(results) == 1

    def test_window_start_greater_than_end_returns_empty(self):
        """window_start_utc > window_end_utc must return empty list, not raise."""
        adapter = _make_adapter()
        _persist_record(adapter, created_utc=5_000_000)
        results = adapter.get_recent_records(window_start_utc=9_000_000, window_end_utc=1_000_000)
        assert results == []

    def test_multiple_records_partial_window(self):
        """Only records within the window are returned when store contains records outside too."""
        adapter = _make_adapter()
        _persist_record(adapter, created_utc=100_000)  # outside
        _persist_record(adapter, created_utc=500_000)  # inside
        _persist_record(adapter, created_utc=600_000)  # inside
        _persist_record(adapter, created_utc=999_999)  # outside

        results = adapter.get_recent_records(400_000, 700_000)
        assert len(results) == 2
        assert all(400_000 <= r.created_utc <= 700_000 for r in results)

    def test_all_records_in_wide_window(self):
        """A window that spans all records returns all of them."""
        adapter = _make_adapter()
        for ts in [100_000, 200_000, 300_000]:
            _persist_record(adapter, created_utc=ts)
        results = adapter.get_recent_records(0, 9_999_999)
        assert len(results) == 3

    def test_preserves_insertion_order(self):
        """get_recent_records returns records in insertion order."""
        adapter = _make_adapter()
        timestamps = [1_000_000, 1_000_100, 1_000_200]
        for ts in timestamps:
            _persist_record(adapter, created_utc=ts)
        results = adapter.get_recent_records(999_999, 1_000_300)
        assert [r.created_utc for r in results] == timestamps

    def test_in_memory_store_get_records_protocol_conformant(self):
        """InMemoryHealingOutcomeIntakeStore.get_records() satisfies the protocol."""
        store = InMemoryHealingOutcomeIntakeStore()
        assert hasattr(store, "get_records") and callable(store.get_records)
        # Before any writes
        assert store.get_records() == []
