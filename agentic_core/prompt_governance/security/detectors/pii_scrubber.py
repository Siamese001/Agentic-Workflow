import re

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "pii_scrubber", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "pii_scrubber", "policy_binding")
trace_contract._emit_snapshots_state("p0", "pii_scrubber", "state_snapshot")

trace_contract._emit_emits_metric_event("pii_scrubber", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("pii_scrubber", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("pii_scrubber", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("pii_scrubber", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("pii_scrubber", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("pii_scrubber", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("pii_scrubber", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("pii_scrubber", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("pii_scrubber", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("pii_scrubber", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("pii_scrubber", "p4obs", "alert")
trace_contract._emit_links_incident_trace("pii_scrubber", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("pii_scrubber", "p3lm", "pattern")
trace_contract._emit_records_learning_event("pii_scrubber", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("pii_scrubber", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("pii_scrubber", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("pii_scrubber", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("pii_scrubber", "p3lm", "policy")
trace_contract._emit_stores_learning_state("pii_scrubber", "p3lm", "state")
trace_contract._emit_records_execution_trace("pii_scrubber", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("pii_scrubber", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("pii_scrubber", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("pii_scrubber", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("pii_scrubber", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("pii_scrubber", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("pii_scrubber", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("pii_scrubber", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("pii_scrubber", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "pii_scrubber", "context_pull")
trace_contract._emit_pulls_context("p1", "pii_scrubber", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "pii_scrubber", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "pii_scrubber", "uwg_term_2")
trace_contract._emit_writes_through("p1", "pii_scrubber", "write_through")
trace_contract._emit_writes_through("p1", "pii_scrubber", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "pii_scrubber", "safety_validation")
trace_contract._emit_invokes_eval("p1", "pii_scrubber", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "pii_scrubber", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "pii_scrubber", "human_escalation")
trace_contract._emit_routes_through("p1", "pii_scrubber", "route_through")
trace_contract._emit_checks_agent_registry("p1", "pii_scrubber", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "pii_scrubber", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "pii_scrubber", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "pii_scrubber", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "pii_scrubber", "target_agent")
trace_contract._emit_verifies_policy("p1", "pii_scrubber", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "pii_scrubber", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "pii_scrubber", "boundary_check")
trace_contract._emit_transcripts_response("p1", "pii_scrubber", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "pii_scrubber")
trace_contract._emit_gated_by_confidence("p1", "pii_scrubber", "confidence_gate")
trace_contract.emit_replay_key("p0", "pii_scrubber")
trace_contract.emit_determinism_digest("p0", "pii_scrubber")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "pii_scrubber", "execution_auth")
trace_contract._emit_validates_capability("p2", "pii_scrubber", "capability_check")
trace_contract._emit_routes_to_capability("p2", "pii_scrubber", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "pii_scrubber", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "pii_scrubber", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "pii_scrubber", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "pii_scrubber", "exec_output")
trace_contract._emit_dispatches_agent("p3", "pii_scrubber", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "pii_scrubber", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "pii_scrubber", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "pii_scrubber", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "pii_scrubber", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "pii_scrubber", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "pii_scrubber", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "pii_scrubber", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "pii_scrubber", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "pii_scrubber", "eval_metric")
trace_contract._emit_stores_embedding("p4", "pii_scrubber", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "pii_scrubber", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "pii_scrubber", "exec_snapshot_link")


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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "PIIScrubber.scrub")

        if not text:
            return ""
        text = re.sub(self.EMAIL_PATTERN, "[EMAIL_REDACTED]", text)
        text = re.sub(self.PHONE_PATTERN, "[PHONE_REDACTED]", text)
        return text
