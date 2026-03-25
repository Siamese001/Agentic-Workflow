"""Unit tests for system_learning.engines.telemetry_consumer."""

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_authorize_and_execute("p2", "test_telemetry_consumer", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_telemetry_consumer", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_telemetry_consumer", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_telemetry_consumer", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_telemetry_consumer", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_telemetry_consumer", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_telemetry_consumer", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_telemetry_consumer", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_telemetry_consumer", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_telemetry_consumer", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_telemetry_consumer", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_telemetry_consumer", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_telemetry_consumer", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_telemetry_consumer", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_telemetry_consumer", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_telemetry_consumer", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_telemetry_consumer", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_telemetry_consumer", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_telemetry_consumer", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_telemetry_consumer", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
from system_learning.engines.telemetry_consumer import (
    TelemetryConsumerError,
    consume_telemetry,
)

# REMOVED: _emit_emits_metric_event("test_telemetry_consumer", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_telemetry_consumer", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_telemetry_consumer", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_telemetry_consumer", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_telemetry_consumer", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_telemetry_consumer", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_telemetry_consumer", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_telemetry_consumer", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_telemetry_consumer", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_telemetry_consumer", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_telemetry_consumer", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_telemetry_consumer", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_telemetry_consumer", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_telemetry_consumer", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_telemetry_consumer", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_telemetry_consumer", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_telemetry_consumer", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_telemetry_consumer", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_telemetry_consumer", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_telemetry_consumer", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_telemetry_consumer", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_telemetry_consumer", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_telemetry_consumer", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_telemetry_consumer", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_telemetry_consumer", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_telemetry_consumer", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_telemetry_consumer", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_telemetry_consumer", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_telemetry_consumer")
# REMOVED: _emit_applies_guardrail("p0", "test_telemetry_consumer", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_telemetry_consumer", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_telemetry_consumer", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_telemetry_consumer", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_telemetry_consumer", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_telemetry_consumer", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_telemetry_consumer", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_telemetry_consumer", "write_through")
# REMOVED: _emit_writes_through("p1", "test_telemetry_consumer", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_telemetry_consumer", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_telemetry_consumer", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_telemetry_consumer", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_telemetry_consumer", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_telemetry_consumer", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_telemetry_consumer", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_telemetry_consumer", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_telemetry_consumer", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_telemetry_consumer", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_telemetry_consumer", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_telemetry_consumer", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_telemetry_consumer", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_telemetry_consumer", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_telemetry_consumer", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_telemetry_consumer")
# REMOVED: _emit_gated_by_confidence("p1", "test_telemetry_consumer", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_telemetry_consumer")
# REMOVED: emit_determinism_digest("p0", "test_telemetry_consumer")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit_min_deps


# =============================================================================
# Fake TelemetryStore
# =============================================================================


class FakeTelemetryStore:
    """In-memory fake telemetry store for testing."""

    def __init__(self, events: list[tuple[int, str, bytes]]):
        self._events = events

    def read_events(self, window_start_utc: int, window_end_utc: int) -> tuple[tuple[int, str, bytes], ...]:
        """Read events within window."""
        # Filter events within window
        filtered = [
            (ts, kind, payload)
            for ts, kind, payload in self._events
            if window_start_utc <= ts < window_end_utc
        ]
        return tuple(filtered)


# =============================================================================
# Tests
# =============================================================================


class TestTelemetryConsumer:
    def test_deterministic_slice_id_across_two_calls(self):
        """Same backing data produces identical slice_id across two calls."""
        events = [
            (1700000000, "metric", b"cpu=50"),
            (1700000100, "metric", b"mem=1000"),
            (1700000200, "error", b"timeout"),
        ]
        store = FakeTelemetryStore(events)

        slice1 = consume_telemetry(store, 1700000000, 1700000300)
        slice2 = consume_telemetry(store, 1700000000, 1700000300)

        assert slice1.slice_id == slice2.slice_id
        assert slice1.slice_hash == slice2.slice_hash
        assert slice1.slice_id == slice1.slice_hash

    def test_sorting_stable_and_canonical(self):
        """Events are sorted deterministically by (ts_utc, kind, payload_hash)."""
        # Create events in non-canonical order
        events = [
            (1700000200, "error", b"timeout"),
            (1700000000, "metric", b"cpu=50"),
            (1700000100, "metric", b"mem=1000"),
        ]
        store = FakeTelemetryStore(events)

        slice_obj = consume_telemetry(store, 1700000000, 1700000300)

        # Events should be sorted by ts_utc
        assert len(slice_obj.events) == 3
        assert slice_obj.events[0].ts_utc == 1700000000
        assert slice_obj.events[1].ts_utc == 1700000100
        assert slice_obj.events[2].ts_utc == 1700000200

    def test_invalid_window_rejected(self):
        """Invalid window (start >= end) raises TelemetryConsumerError."""
        store = FakeTelemetryStore([])

        with pytest.raises(TelemetryConsumerError, match="Invalid window"):
            consume_telemetry(store, 1700003600, 1700000000)

    def test_empty_window_produces_empty_slice(self):
        """Empty window produces slice with no events."""
        events = [
            (1700000000, "metric", b"cpu=50"),
        ]
        store = FakeTelemetryStore(events)

        # Window that excludes all events
        slice_obj = consume_telemetry(store, 1700010000, 1700020000)

        assert len(slice_obj.events) == 0

    def test_window_filtering(self):
        """Events outside window are excluded."""
        events = [
            (1700000000, "metric", b"cpu=50"),  # Before window
            (1700001000, "metric", b"mem=1000"),  # In window
            (1700002000, "error", b"timeout"),  # In window
            (1700005000, "metric", b"cpu=60"),  # After window
        ]
        store = FakeTelemetryStore(events)

        slice_obj = consume_telemetry(store, 1700001000, 1700003000)

        # Only 2 events should be in slice
        assert len(slice_obj.events) == 2
        assert slice_obj.events[0].ts_utc == 1700001000
        assert slice_obj.events[1].ts_utc == 1700002000

    def test_payload_hash_computed(self):
        """payload_hash is SHA-256 of payload bytes."""
        events = [
            (1700000000, "metric", b"test_payload"),
        ]
        store = FakeTelemetryStore(events)

        slice_obj = consume_telemetry(store, 1700000000, 1700001000)

        # payload_hash should be a valid SHA-256 hex digest
        assert len(slice_obj.events) == 1
        payload_hash = slice_obj.events[0].payload_hash
        assert len(payload_hash) == 64
        assert all(c in "0123456789abcdef" for c in payload_hash)

    def test_same_timestamp_different_kind_sorted(self):
        """Events with same timestamp are sorted by kind."""
        events = [
            (1700000000, "zzz", b"payload1"),
            (1700000000, "aaa", b"payload2"),
            (1700000000, "mmm", b"payload3"),
        ]
        store = FakeTelemetryStore(events)

        slice_obj = consume_telemetry(store, 1700000000, 1700001000)

        # Should be sorted alphabetically by kind
        assert slice_obj.events[0].kind == "aaa"
        assert slice_obj.events[1].kind == "mmm"
        assert slice_obj.events[2].kind == "zzz"


class TestDeterminism:
    def test_consume_telemetry_deterministic(self):
        """consume_telemetry produces identical results across multiple calls."""
        events = [
            (1700000000, "metric", b"cpu=50"),
            (1700000100, "metric", b"mem=1000"),
            (1700000200, "error", b"timeout"),
        ]
        store = FakeTelemetryStore(events)

        slice1 = consume_telemetry(store, 1700000000, 1700000300)
        slice2 = consume_telemetry(store, 1700000000, 1700000300)
        slice3 = consume_telemetry(store, 1700000000, 1700000300)

        assert slice1.slice_id == slice2.slice_id == slice3.slice_id
        assert slice1.slice_hash == slice2.slice_hash == slice3.slice_hash
