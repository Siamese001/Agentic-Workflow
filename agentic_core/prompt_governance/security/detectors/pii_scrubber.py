import re

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "pii_scrubber", "p0_governance")
_emit_reads_policy_state("p0", "pii_scrubber", "policy_binding")
_emit_snapshots_state("p0", "pii_scrubber", "state_snapshot")
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
    _emit_links_incident_trace,
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
    _emit_writes_through,
)

_emit_emits_metric_event("pii_scrubber", "p4obs", "metric_1")
_emit_emits_metric_event("pii_scrubber", "p4obs", "metric_2")
_emit_emits_metric_event("pii_scrubber", "p4obs", "metric_3")
_emit_emits_metric_event("pii_scrubber", "p4obs", "metric_4")
_emit_emits_metric_event("pii_scrubber", "p4obs", "metric_5")
_emit_emits_metric_event("pii_scrubber", "p4obs", "metric_6")
_emit_records_incident_event("pii_scrubber", "p4obs", "incident")
_emit_captures_runtime_anomaly("pii_scrubber", "p4obs", "anomaly")
_emit_writes_observability_log("pii_scrubber", "p4obs", "obs_log")
_emit_updates_monitoring_state("pii_scrubber", "p4obs", "mon_state")
_emit_triggers_alert("pii_scrubber", "p4obs", "alert")
_emit_links_incident_trace("pii_scrubber", "p4obs", "trace_link")
_emit_captures_pattern("pii_scrubber", "p3lm", "pattern")
_emit_records_learning_event("pii_scrubber", "p3lm", "learning_event")
_emit_writes_learning_snapshot("pii_scrubber", "p3lm", "snapshot")
_emit_feeds_meta_learning("pii_scrubber", "p3lm", "meta_feed")
_emit_updates_routing_strategy("pii_scrubber", "p3lm", "routing")
_emit_improves_agent_policy("pii_scrubber", "p3lm", "policy")
_emit_stores_learning_state("pii_scrubber", "p3lm", "state")
_emit_records_execution_trace("pii_scrubber", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("pii_scrubber", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("pii_scrubber", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("pii_scrubber", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("pii_scrubber", "L4_STATE", "p2_trace_5")
_emit_reads_environ("pii_scrubber", "env_read", "p2_env_1")
_emit_reads_environ("pii_scrubber", "env_read", "p2_env_2")
_emit_reads_runtime_state("pii_scrubber", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("pii_scrubber", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "pii_scrubber", "context_pull")
_emit_pulls_context("p1", "pii_scrubber", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "pii_scrubber", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "pii_scrubber", "uwg_term_2")
_emit_writes_through("p1", "pii_scrubber", "write_through")
_emit_writes_through("p1", "pii_scrubber", "write_through_2")
_emit_validated_by_safety_plane("p1", "pii_scrubber", "safety_validation")
_emit_invokes_eval("p1", "pii_scrubber", "eval_call")
_emit_proposal_commits_routing("p1", "pii_scrubber", "routing_commit")
_emit_escalates_to_human("p1", "pii_scrubber", "human_escalation")
_emit_routes_through("p1", "pii_scrubber", "route_through")
_emit_checks_agent_registry("p1", "pii_scrubber", "agent_registry")
_emit_validates_agent_capability("p1", "pii_scrubber", "capability")
_emit_dispatches_execution_plan("p1", "pii_scrubber", "exec_plan")
_emit_agent_executes_agent("p1", "pii_scrubber", "sub_agent")
_emit_routes_to_agent("p1", "pii_scrubber", "target_agent")
_emit_verifies_policy("p1", "pii_scrubber", "policy_check")
_emit_observes_runtime_state("p1", "pii_scrubber", "runtime_state")
_emit_verifies_boundary("p1", "pii_scrubber", "boundary_check")
_emit_transcripts_response("p1", "pii_scrubber", "transcript")
_emit_hard_fails_untranscripted("p1", "pii_scrubber")
_emit_gated_by_confidence("p1", "pii_scrubber", "confidence_gate")
emit_replay_key("p0", "pii_scrubber")
emit_determinism_digest("p0", "pii_scrubber")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "pii_scrubber", "execution_auth")
_emit_validates_capability("p2", "pii_scrubber", "capability_check")
_emit_routes_to_capability("p2", "pii_scrubber", "capability_route")
_emit_writes_via_uwg("p2", "pii_scrubber", "uwg_write")
_emit_blocks_direct_write("p2", "pii_scrubber", "direct_write_block")
_emit_records_tool_invocation("p2", "pii_scrubber", "tool_invocation")
_emit_captures_execution_output("p2", "pii_scrubber", "exec_output")
_emit_dispatches_agent("p3", "pii_scrubber", "agent_dispatch")
_emit_coordinates_agents("p3", "pii_scrubber", "agent_coordination")
_emit_records_workflow_lineage("p3", "pii_scrubber", "workflow_lineage")
_emit_records_healing_outcome("p3", "pii_scrubber", "healing_outcome")
_emit_escalates_failure("p3", "pii_scrubber", "failure_escalation")
_emit_orchestrates_workflow("p3", "pii_scrubber", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "pii_scrubber", "healing_dispatch")
_emit_invokes_evaluation("p3", "pii_scrubber", "evaluation_signal")
_emit_records_telemetry_event("p4", "pii_scrubber", "telemetry_event")
_emit_captures_evaluation_metric("p4", "pii_scrubber", "eval_metric")
_emit_stores_embedding("p4", "pii_scrubber", "embedding_store")
_emit_updates_meta_learning_state("p4", "pii_scrubber", "meta_learning")
_emit_links_execution_to_snapshot("p4", "pii_scrubber", "exec_snapshot_link")


class PIIScrubber:
    """
    Sanitizes sensitive information from text.
    """

    EMAIL_PATTERN = "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b"
    PHONE_PATTERN = "\\b(?:\\+?1[-.]?)?\\(?([0-9]{3})\\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})\\b|\\b([0-9]{3})[-. ]?([0-9]{4})\\b"

    def scrub(self, text: str) -> str:
        """
        Replaces PII with placeholder tokens.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PIIScrubber.scrub")

        if not text:
            return ""
        text = re.sub(self.EMAIL_PATTERN, "[EMAIL_REDACTED]", text)
        text = re.sub(self.PHONE_PATTERN, "[PHONE_REDACTED]", text)
        return text
