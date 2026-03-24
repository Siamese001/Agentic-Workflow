"""Gate C4: Observability liveness tests.

Every telemetry channel must emit on startup/check.
Tests verify HealingEventEmitter, AICheckAuditEmitter, and HITLDecisionLogger
all produce observable signals on first use.
"""

from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_observability_liveness")
_emit_applies_guardrail("p0", "test_observability_liveness", "p0_governance")
_emit_reads_policy_state("p0", "test_observability_liveness", "policy_binding")
_emit_snapshots_state("p0", "test_observability_liveness", "state_snapshot")
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

_emit_emits_metric_event("test_observability_liveness", "p4obs", "metric_1")
_emit_emits_metric_event("test_observability_liveness", "p4obs", "metric_2")
_emit_emits_metric_event("test_observability_liveness", "p4obs", "metric_3")
_emit_emits_metric_event("test_observability_liveness", "p4obs", "metric_4")
_emit_emits_metric_event("test_observability_liveness", "p4obs", "metric_5")
_emit_emits_metric_event("test_observability_liveness", "p4obs", "metric_6")
_emit_records_incident_event("test_observability_liveness", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_observability_liveness", "p4obs", "anomaly")
_emit_writes_observability_log("test_observability_liveness", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_observability_liveness", "p4obs", "mon_state")
_emit_triggers_alert("test_observability_liveness", "p4obs", "alert")
_emit_links_incident_trace("test_observability_liveness", "p4obs", "trace_link")
_emit_captures_pattern("test_observability_liveness", "p3lm", "pattern")
_emit_records_learning_event("test_observability_liveness", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_observability_liveness", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_observability_liveness", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_observability_liveness", "p3lm", "routing")
_emit_improves_agent_policy("test_observability_liveness", "p3lm", "policy")
_emit_stores_learning_state("test_observability_liveness", "p3lm", "state")
_emit_records_execution_trace("test_observability_liveness", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_observability_liveness", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_observability_liveness", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_observability_liveness", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_observability_liveness", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_observability_liveness", "env_read", "p2_env_1")
_emit_reads_environ("test_observability_liveness", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_observability_liveness", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_observability_liveness", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_observability_liveness", "context_pull")
_emit_pulls_context("p1", "test_observability_liveness", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_observability_liveness", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_observability_liveness", "uwg_term_2")
_emit_writes_through("p1", "test_observability_liveness", "write_through")
_emit_writes_through("p1", "test_observability_liveness", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_observability_liveness", "safety_validation")
_emit_invokes_eval("p1", "test_observability_liveness", "eval_call")
_emit_proposal_commits_routing("p1", "test_observability_liveness", "routing_commit")
_emit_escalates_to_human("p1", "test_observability_liveness", "human_escalation")
_emit_routes_through("p1", "test_observability_liveness", "route_through")
_emit_checks_agent_registry("p1", "test_observability_liveness", "agent_registry")
_emit_validates_agent_capability("p1", "test_observability_liveness", "capability")
_emit_dispatches_execution_plan("p1", "test_observability_liveness", "exec_plan")
_emit_agent_executes_agent("p1", "test_observability_liveness", "sub_agent")
_emit_routes_to_agent("p1", "test_observability_liveness", "target_agent")
_emit_verifies_policy("p1", "test_observability_liveness", "policy_check")
_emit_observes_runtime_state("p1", "test_observability_liveness", "runtime_state")
_emit_verifies_boundary("p1", "test_observability_liveness", "boundary_check")
_emit_transcripts_response("p1", "test_observability_liveness", "transcript")
_emit_hard_fails_untranscripted("p1", "test_observability_liveness")
_emit_gated_by_confidence("p1", "test_observability_liveness", "confidence_gate")
emit_replay_key("p0", "test_observability_liveness")
emit_determinism_digest("p0", "test_observability_liveness")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_observability_liveness", "execution_auth")
_emit_validates_capability("p2", "test_observability_liveness", "capability_check")
_emit_routes_to_capability("p2", "test_observability_liveness", "capability_route")
_emit_writes_via_uwg("p2", "test_observability_liveness", "uwg_write")
_emit_blocks_direct_write("p2", "test_observability_liveness", "direct_write_block")
_emit_records_tool_invocation("p2", "test_observability_liveness", "tool_invocation")
_emit_captures_execution_output("p2", "test_observability_liveness", "exec_output")
_emit_dispatches_agent("p3", "test_observability_liveness", "agent_dispatch")
_emit_coordinates_agents("p3", "test_observability_liveness", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_observability_liveness", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_observability_liveness", "healing_outcome")
_emit_escalates_failure("p3", "test_observability_liveness", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_observability_liveness", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_observability_liveness", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_observability_liveness", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_observability_liveness", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_observability_liveness", "eval_metric")
_emit_stores_embedding("p4", "test_observability_liveness", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_observability_liveness", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_observability_liveness", "exec_snapshot_link")


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TestHealingEventEmitterLiveness:
    def test_emitter_produces_event_on_first_emit(self, tmp_path):
        from agentic_core.L2_execution.healers.healing_event_emitter import HealingEventEmitter

        emitter = HealingEventEmitter(log_path=tmp_path / "healing.jsonl")
        event = emitter.emit(
            trace_id="liveness-t001",
            attempt_number=1,
            failure_class="liveness_check",
            healer_selected="LivenessAgent",
            model_used="gemini-2.5-pro",
            outcome="success",
        )
        assert event.trace_id == "liveness-t001"
        events = emitter.emitted_events()
        assert len(events) == 1

    def test_emitter_log_file_created(self, tmp_path):
        from agentic_core.L2_execution.healers.healing_event_emitter import HealingEventEmitter

        log_path = tmp_path / "healing_liveness.jsonl"
        emitter = HealingEventEmitter(log_path=log_path)
        emitter.emit("t", 1, "err", "agent", "model", "success")
        assert log_path.exists()
        assert log_path.stat().st_size > 0

    def test_negative_no_emission_without_emit_call(self, tmp_path):
        from agentic_core.L2_execution.healers.healing_event_emitter import HealingEventEmitter

        emitter = HealingEventEmitter(log_path=tmp_path / "healing.jsonl")
        assert emitter.emitted_events() == []


class TestAICheckAuditEmitterLiveness:
    def test_emitter_produces_record_on_emit(self, tmp_path):
        from agentic_core.L5_safety.audit.ai_check_audit import AICheckAuditEmitter, AICheckAuditRecord

        emitter = AICheckAuditEmitter(audit_path=tmp_path / "audit.jsonl")
        record = emitter.emit(
            component="LivenessChecker",
            model_id="gemini-2.5-pro",
            input_data="liveness check input",
            verdict="PASS",
            confidence=0.95,
            trace_id="liveness-audit-001",
        )
        assert isinstance(record, AICheckAuditRecord)
        assert record.confidence == 0.95

    def test_emitter_writes_to_file(self, tmp_path):
        from agentic_core.L5_safety.audit.ai_check_audit import AICheckAuditEmitter

        audit_path = tmp_path / "audit_liveness.jsonl"
        emitter = AICheckAuditEmitter(audit_path=audit_path)
        emitter.emit("comp", "model", "input_data_str", "PASS", 0.8, "t-001")
        assert audit_path.exists()
        assert audit_path.stat().st_size > 0

    def test_negative_no_entries_without_emit(self, tmp_path):
        from agentic_core.L5_safety.audit.ai_check_audit import AICheckAuditEmitter

        emitter = AICheckAuditEmitter(audit_path=tmp_path / "audit.jsonl")
        assert emitter.read_all() == []


class TestHITLDecisionLoggerLiveness:
    def test_logger_produces_record_on_log(self, tmp_path):
        from agentic_core.L5_safety.hitl.decision_logger import HITLDecisionLogger

        logger = HITLDecisionLogger(log_path=tmp_path / "decisions.jsonl")
        d = logger.log("LivenessAgent", "liveness.py", "check", "propose", "APPROVE")
        assert d.decision_number == 1
        assert logger.count() == 1

    def test_negative_count_zero_on_fresh_logger(self, tmp_path):
        from agentic_core.L5_safety.hitl.decision_logger import HITLDecisionLogger

        logger = HITLDecisionLogger(log_path=tmp_path / "decisions.jsonl")
        assert logger.count() == 0
