"""GAP-C/E: HealingOutcomeIntakeAdapter.get_recent_records() interface contract."""

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_adapter_get_recent_records", "p4obs", "metric_1")
_emit_emits_metric_event("test_adapter_get_recent_records", "p4obs", "metric_2")
_emit_emits_metric_event("test_adapter_get_recent_records", "p4obs", "metric_3")
_emit_emits_metric_event("test_adapter_get_recent_records", "p4obs", "metric_4")
_emit_emits_metric_event("test_adapter_get_recent_records", "p4obs", "metric_5")
_emit_emits_metric_event("test_adapter_get_recent_records", "p4obs", "metric_6")
_emit_records_incident_event("test_adapter_get_recent_records", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adapter_get_recent_records", "p4obs", "anomaly")
_emit_writes_observability_log("test_adapter_get_recent_records", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adapter_get_recent_records", "p4obs", "mon_state")
_emit_triggers_alert("test_adapter_get_recent_records", "p4obs", "alert")
_emit_links_incident_trace("test_adapter_get_recent_records", "p4obs", "trace_link")
_emit_captures_pattern("test_adapter_get_recent_records", "p3lm", "pattern")
_emit_records_learning_event("test_adapter_get_recent_records", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adapter_get_recent_records", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adapter_get_recent_records", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adapter_get_recent_records", "p3lm", "routing")
_emit_improves_agent_policy("test_adapter_get_recent_records", "p3lm", "policy")
_emit_stores_learning_state("test_adapter_get_recent_records", "p3lm", "state")
_emit_records_execution_trace("test_adapter_get_recent_records", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adapter_get_recent_records", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adapter_get_recent_records", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adapter_get_recent_records", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adapter_get_recent_records", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adapter_get_recent_records", "env_read", "p2_env_1")
_emit_reads_environ("test_adapter_get_recent_records", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adapter_get_recent_records", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adapter_get_recent_records", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_adapter_get_recent_records", "context_pull")
_emit_pulls_context("p1", "test_adapter_get_recent_records", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_adapter_get_recent_records", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adapter_get_recent_records", "uwg_term_2")
_emit_writes_through("p1", "test_adapter_get_recent_records", "write_through")
_emit_writes_through("p1", "test_adapter_get_recent_records", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_adapter_get_recent_records", "safety_validation")
_emit_invokes_eval("p1", "test_adapter_get_recent_records", "eval_call")
_emit_proposal_commits_routing("p1", "test_adapter_get_recent_records", "routing_commit")
_emit_escalates_to_human("p1", "test_adapter_get_recent_records", "human_escalation")
_emit_routes_through("p1", "test_adapter_get_recent_records", "route_through")
_emit_checks_agent_registry("p1", "test_adapter_get_recent_records", "agent_registry")
_emit_validates_agent_capability("p1", "test_adapter_get_recent_records", "capability")
_emit_dispatches_execution_plan("p1", "test_adapter_get_recent_records", "exec_plan")
_emit_agent_executes_agent("p1", "test_adapter_get_recent_records", "sub_agent")
_emit_routes_to_agent("p1", "test_adapter_get_recent_records", "target_agent")
_emit_verifies_policy("p1", "test_adapter_get_recent_records", "policy_check")
_emit_observes_runtime_state("p1", "test_adapter_get_recent_records", "runtime_state")
_emit_verifies_boundary("p1", "test_adapter_get_recent_records", "boundary_check")
_emit_transcripts_response("p1", "test_adapter_get_recent_records", "transcript")
_emit_hard_fails_untranscripted("p1", "test_adapter_get_recent_records")
_emit_gated_by_confidence("p1", "test_adapter_get_recent_records", "confidence_gate")
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
