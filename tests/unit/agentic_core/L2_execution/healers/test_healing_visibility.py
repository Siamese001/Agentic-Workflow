"""Addendum 1.3: Healing Visibility Enforcement tests."""

from __future__ import annotations

from agentic_core.L2_execution.healers.healing_event_emitter import (
    HealingAttemptEvent,
    HealingEventEmitter,
)
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_healing_visibility")
# REMOVED: _emit_applies_guardrail("p0", "test_healing_visibility", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_healing_visibility", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_healing_visibility", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_healing_visibility", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_healing_visibility", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_healing_visibility", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_healing_visibility", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_healing_visibility", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_healing_visibility", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_healing_visibility", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_healing_visibility", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_healing_visibility", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_healing_visibility", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_healing_visibility", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_healing_visibility", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_healing_visibility", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_healing_visibility", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_healing_visibility", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_healing_visibility", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_healing_visibility", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_healing_visibility", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_healing_visibility", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_healing_visibility", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_healing_visibility", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_healing_visibility", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_healing_visibility", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_healing_visibility", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_healing_visibility", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_healing_visibility", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_healing_visibility", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_healing_visibility", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_healing_visibility", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_healing_visibility", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_healing_visibility", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_healing_visibility", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_healing_visibility", "write_through")
# REMOVED: _emit_writes_through("p1", "test_healing_visibility", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_healing_visibility", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_healing_visibility", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_healing_visibility", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_healing_visibility", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_healing_visibility", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_healing_visibility", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_healing_visibility", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_healing_visibility", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_healing_visibility", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_healing_visibility", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_healing_visibility", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_healing_visibility", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_healing_visibility", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_healing_visibility", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_healing_visibility")
# REMOVED: _emit_gated_by_confidence("p1", "test_healing_visibility", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_healing_visibility")
# REMOVED: emit_determinism_digest("p0", "test_healing_visibility")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_healing_visibility", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_healing_visibility", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_healing_visibility", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_healing_visibility", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_healing_visibility", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_healing_visibility", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_healing_visibility", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_healing_visibility", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_healing_visibility", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_healing_visibility", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_healing_visibility", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_healing_visibility", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_healing_visibility", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_healing_visibility", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_healing_visibility", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_healing_visibility", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_healing_visibility", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_healing_visibility", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_healing_visibility", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_healing_visibility", "exec_snapshot_link")


class TestHealingEventEmitter:
    def test_emit_returns_event(self, tmp_path):
        emitter = HealingEventEmitter(log_path=tmp_path / "events.jsonl")
        event = emitter.emit(
            trace_id="t-001",
            attempt_number=1,
            failure_class="syntax_error",
            healer_selected="LocalAgent",
            model_used="gemini-2.5-pro",
            outcome="success",
        )
        assert isinstance(event, HealingAttemptEvent)
        assert event.trace_id == "t-001"
        assert event.attempt_number == 1
        assert event.outcome == "success"

    def test_emitted_events_list_grows(self, tmp_path):
        emitter = HealingEventEmitter(log_path=tmp_path / "events.jsonl")
        emitter.emit("t-001", 1, "type_error", "LocalAgent", "gpt-4", "success")
        emitter.emit("t-001", 2, "type_error", "QwenVLLM", "qwen2.5", "error")
        assert len(emitter.emitted_events()) == 2

    def test_event_written_to_jsonl(self, tmp_path):
        log_path = tmp_path / "events.jsonl"
        emitter = HealingEventEmitter(log_path=log_path)
        emitter.emit("t-002", 1, "import_error", "LocalAgent", "gemini", "partial")
        assert log_path.exists()
        lines = log_path.read_text().strip().splitlines()
        assert len(lines) == 1
        import json

        record = json.loads(lines[0])
        assert record["trace_id"] == "t-002"
        assert record["outcome"] == "partial"

    def test_multiple_events_separate_lines(self, tmp_path):
        log_path = tmp_path / "events.jsonl"
        emitter = HealingEventEmitter(log_path=log_path)
        for i in range(3):
            emitter.emit(f"t-{i:03d}", i, "err", "agent", "model", "success")
        lines = log_path.read_text().strip().splitlines()
        assert len(lines) == 3

    def test_negative_no_event_without_emit(self, tmp_path):
        """Negative control: no events unless emit() is called."""
        emitter = HealingEventEmitter(log_path=tmp_path / "events.jsonl")
        assert emitter.emitted_events() == []

    def test_metadata_stored(self, tmp_path):
        emitter = HealingEventEmitter(log_path=tmp_path / "events.jsonl")
        event = emitter.emit(
            "t-meta",
            1,
            "err",
            "agent",
            "model",
            "success",
            metadata={"file": "foo.py", "line": 42},
        )
        assert event.metadata == {"file": "foo.py", "line": 42}
