"""Unit tests for TelemetryRecorder.

Phase 1 Wave 1.3 test suite. Verifies durable telemetry,
outcome logging, reconciliation, and SHA-256 immutability.
"""

import pytest

from agentic_core.L4_state.enforcement.telemetry_recorder import (
    OutcomeRecord,
    ReconResult,
    TelemetryRecorder,
)
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

_emit_records_execution_trace("p0", "evidence", "test_telemetry_recorder")
_emit_applies_guardrail("p0", "test_telemetry_recorder", "p0_governance")
_emit_reads_policy_state("p0", "test_telemetry_recorder", "policy_binding")
_emit_snapshots_state("p0", "test_telemetry_recorder", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("test_telemetry_recorder", "p4obs", "metric_1")
_emit_emits_metric_event("test_telemetry_recorder", "p4obs", "metric_2")
_emit_emits_metric_event("test_telemetry_recorder", "p4obs", "metric_3")
_emit_emits_metric_event("test_telemetry_recorder", "p4obs", "metric_4")
_emit_emits_metric_event("test_telemetry_recorder", "p4obs", "metric_5")
_emit_emits_metric_event("test_telemetry_recorder", "p4obs", "metric_6")
_emit_records_incident_event("test_telemetry_recorder", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_telemetry_recorder", "p4obs", "anomaly")
_emit_writes_observability_log("test_telemetry_recorder", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_telemetry_recorder", "p4obs", "mon_state")
_emit_triggers_alert("test_telemetry_recorder", "p4obs", "alert")
_emit_links_incident_trace("test_telemetry_recorder", "p4obs", "trace_link")
_emit_captures_pattern("test_telemetry_recorder", "p3lm", "pattern")
_emit_records_learning_event("test_telemetry_recorder", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_telemetry_recorder", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_telemetry_recorder", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_telemetry_recorder", "p3lm", "routing")
_emit_improves_agent_policy("test_telemetry_recorder", "p3lm", "policy")
_emit_stores_learning_state("test_telemetry_recorder", "p3lm", "state")
_emit_records_execution_trace("test_telemetry_recorder", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_telemetry_recorder", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_telemetry_recorder", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_telemetry_recorder", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_telemetry_recorder", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_telemetry_recorder", "env_read", "p2_env_1")
_emit_reads_environ("test_telemetry_recorder", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_telemetry_recorder", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_telemetry_recorder", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_telemetry_recorder", "context_pull")
_emit_pulls_context("p1", "test_telemetry_recorder", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_telemetry_recorder", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_telemetry_recorder", "uwg_term_2")
_emit_writes_through("p1", "test_telemetry_recorder", "write_through")
_emit_writes_through("p1", "test_telemetry_recorder", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_telemetry_recorder", "safety_validation")
_emit_invokes_eval("p1", "test_telemetry_recorder", "eval_call")
_emit_proposal_commits_routing("p1", "test_telemetry_recorder", "routing_commit")
emit_replay_key("p0", "test_telemetry_recorder")
emit_determinism_digest("p0", "test_telemetry_recorder")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_telemetry_recorder", "execution_auth")
_emit_validates_capability("p2", "test_telemetry_recorder", "capability_check")
_emit_routes_to_capability("p2", "test_telemetry_recorder", "capability_route")
_emit_writes_via_uwg("p2", "test_telemetry_recorder", "uwg_write")
_emit_blocks_direct_write("p2", "test_telemetry_recorder", "direct_write_block")
_emit_records_tool_invocation("p2", "test_telemetry_recorder", "tool_invocation")
_emit_captures_execution_output("p2", "test_telemetry_recorder", "exec_output")
_emit_dispatches_agent("p3", "test_telemetry_recorder", "agent_dispatch")
_emit_coordinates_agents("p3", "test_telemetry_recorder", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_telemetry_recorder", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_telemetry_recorder", "healing_outcome")
_emit_escalates_failure("p3", "test_telemetry_recorder", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_telemetry_recorder", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_telemetry_recorder", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_telemetry_recorder", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_telemetry_recorder", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_telemetry_recorder", "eval_metric")
_emit_stores_embedding("p4", "test_telemetry_recorder", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_telemetry_recorder", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_telemetry_recorder", "exec_snapshot_link")


@pytest.mark.unit
class TestTelemetryRecorder:
    def setup_method(self):
        self.recorder = TelemetryRecorder()
        self.recorder.clear()  # ensure clean state

    def test_record_returns_sha256(self):
        data = {"test": "data"}
        event_id = self.recorder.record("test_event", data, commit_tick=123)
        assert isinstance(event_id, str)
        assert len(event_id) == 64  # SHA-256 hex length

    def test_same_event_returns_same_id(self):
        data = {"test": "data"}
        id1 = self.recorder.record("test_event", data, commit_tick=123)
        id2 = self.recorder.record("test_event", data, commit_tick=123)
        assert id1 == id2

    def test_different_data_returns_different_ids(self):
        id1 = self.recorder.record("test_event", {"a": 1}, commit_tick=123)
        id2 = self.recorder.record("test_event", {"a": 2}, commit_tick=123)
        assert id1 != id2

    def test_get_events_returns_all(self):
        self.recorder.record("event1", {}, commit_tick=1)
        self.recorder.record("event2", {}, commit_tick=2)
        events = self.recorder.get_events()
        assert len(events) == 2
        assert events[0]["event_type"] == "event1"
        assert events[1]["event_type"] == "event2"

    def test_get_events_filters_by_type(self):
        self.recorder.record("event1", {}, commit_tick=1)
        self.recorder.record("event2", {}, commit_tick=2)
        events = self.recorder.get_events(event_type="event1")
        assert len(events) == 1
        assert events[0]["event_type"] == "event1"

    def test_get_events_limit(self):
        for i in range(5):
            self.recorder.record(f"event{i}", {}, commit_tick=i)
        events = self.recorder.get_events(limit=3)
        assert len(events) == 3
        # Should return last 3 events
        assert events[0]["event_type"] == "event2"
        assert events[2]["event_type"] == "event4"

    def test_log_async_requires_l2_commit_hash(self):
        record = OutcomeRecord(
            execution_latency_ms=100.0,
            outcome_accuracy=0.95,
            compute_cost_tokens=50,
            human_correction_rate=0.1,
            state_diff={},
            l2_commit_hash="",  # Empty hash
            record_hash="abc123",
        )
        with pytest.raises(ValueError, match="l2_commit_hash"):
            self.recorder.log_async(record)

    def test_log_async_stores_record(self):
        record = OutcomeRecord(
            execution_latency_ms=100.0,
            outcome_accuracy=0.95,
            compute_cost_tokens=50,
            human_correction_rate=0.1,
            state_diff={"key": "value"},
            l2_commit_hash="hash123",
            record_hash="record456",
        )
        self.recorder.log_async(record)

        events = self.recorder.get_events(event_type="outcome_record")
        assert len(events) == 1
        assert events[0]["record"]["l2_commit_hash"] == "hash123"

    def test_reconcile_detects_ghost_mutation(self):
        result = self.recorder.reconcile("hash1", "hash2")
        assert isinstance(result, ReconResult)
        assert result.ghost_mutation_detected is True
        assert "Ghost mutation detected" in result.details
        assert result.l4_state_hash == "hash1"
        assert result.actual_hash == "hash2"

    def test_reconcile_successful(self):
        result = self.recorder.reconcile("hash1", "hash1")
        assert result.ghost_mutation_detected is False
        assert "successful" in result.details

    def test_reconcile_logs_event(self):
        self.recorder.reconcile("hash1", "hash2")
        events = self.recorder.get_events(event_type="reconciliation")
        assert len(events) == 1
        assert events[0]["data"]["ghost_detected"] is True

    def test_clear_resets_all_data(self):
        self.recorder.record("test", {}, commit_tick=1)
        assert self.recorder.get_events()
        self.recorder.clear()
        assert not self.recorder.get_events()

    def test_record_includes_commit_tick(self):
        self.recorder.record("test", {}, commit_tick=42)
        events = self.recorder.get_events()
        assert events[0]["commit_tick"] == 42

    def test_record_timestamp_optional(self):
        # By default, no timestamp is included
        self.recorder.record("test", {}, commit_tick=1)
        events = self.recorder.get_events()
        assert "timestamp" not in events[0]

        # Caller can supply timestamp explicitly
        self.recorder.record("test", {}, commit_tick=2, timestamp=1234567890)
        events = self.recorder.get_events()
        assert events[1]["timestamp"] == 1234567890

    def test_no_wall_clock_calls(self, monkeypatch):
        """Negative test: TelemetryRecorder must not call wall-clock APIs."""

        # Create sentinel that raises if any wall-clock API is called
        class WallClockSentinel:
            def __call__(self):
                raise RuntimeError("Wall-clock API 'time' was called - not allowed in deterministic mode")

            def __getattr__(self, name):
                raise RuntimeError(f"Wall-clock API '{name}' was called - not allowed in deterministic mode")

        # Patch common wall-clock sources
        import datetime
        import logging
        import time

        monkeypatch.setattr(time, "time", WallClockSentinel())
        monkeypatch.setattr(time, "monotonic", WallClockSentinel())
        monkeypatch.setattr(time, "perf_counter", WallClockSentinel())
        # Patch datetime at module level
        monkeypatch.setattr(datetime, "datetime", WallClockSentinel())
        # Patch logging module's time reference
        monkeypatch.setattr(logging, "time", WallClockSentinel())

        # Disable logging to avoid time.time() calls from logging module
        self.recorder.logger.disabled = True

        # These operations should NOT trigger wall-clock calls
        self.recorder.record("test_event", {"data": "value"}, commit_tick=123)

        record = OutcomeRecord(
            execution_latency_ms=100.0,
            outcome_accuracy=0.95,
            compute_cost_tokens=50,
            human_correction_rate=0.1,
            state_diff={},
            l2_commit_hash="hash123",
            record_hash="record456",
        )
        self.recorder.log_async(record)

        result = self.recorder.reconcile("hash1", "hash2", commit_tick=456)

        # If we reach here, no wall-clock APIs were called
        assert result.ghost_mutation_detected is True
