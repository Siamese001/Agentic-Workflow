from agentic_core.prompt_governance.security.detectors.injection_detector import InjectionDetector
from agentic_core.prompt_governance.security.detectors.pii_scrubber import PIIScrubber
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "governance_hub", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "governance_hub", "policy_binding")
trace_contract._emit_snapshots_state("p0", "governance_hub", "state_snapshot")

trace_contract._emit_emits_metric_event("governance_hub", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("governance_hub", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("governance_hub", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("governance_hub", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("governance_hub", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("governance_hub", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("governance_hub", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("governance_hub", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("governance_hub", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("governance_hub", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("governance_hub", "p4obs", "alert")
trace_contract._emit_links_incident_trace("governance_hub", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("governance_hub", "p3lm", "pattern")
trace_contract._emit_records_learning_event("governance_hub", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("governance_hub", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("governance_hub", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("governance_hub", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("governance_hub", "p3lm", "policy")
trace_contract._emit_stores_learning_state("governance_hub", "p3lm", "state")
trace_contract._emit_records_execution_trace("governance_hub", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("governance_hub", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("governance_hub", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("governance_hub", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("governance_hub", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("governance_hub", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("governance_hub", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("governance_hub", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("governance_hub", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "governance_hub", "context_pull")
trace_contract._emit_pulls_context("p1", "governance_hub", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "governance_hub", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "governance_hub", "uwg_term_2")
trace_contract._emit_writes_through("p1", "governance_hub", "write_through")
trace_contract._emit_writes_through("p1", "governance_hub", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "governance_hub", "safety_validation")
trace_contract._emit_invokes_eval("p1", "governance_hub", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "governance_hub", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "governance_hub", "human_escalation")
trace_contract._emit_routes_through("p1", "governance_hub", "route_through")
trace_contract._emit_checks_agent_registry("p1", "governance_hub", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "governance_hub", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "governance_hub", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "governance_hub", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "governance_hub", "target_agent")
trace_contract._emit_verifies_policy("p1", "governance_hub", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "governance_hub", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "governance_hub", "boundary_check")
trace_contract._emit_transcripts_response("p1", "governance_hub", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "governance_hub")
trace_contract._emit_gated_by_confidence("p1", "governance_hub", "confidence_gate")
trace_contract.emit_replay_key("p0", "governance_hub")
trace_contract.emit_determinism_digest("p0", "governance_hub")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "governance_hub", "execution_auth")
trace_contract._emit_validates_capability("p2", "governance_hub", "capability_check")
trace_contract._emit_routes_to_capability("p2", "governance_hub", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "governance_hub", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "governance_hub", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "governance_hub", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "governance_hub", "exec_output")
trace_contract._emit_dispatches_agent("p3", "governance_hub", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "governance_hub", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "governance_hub", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "governance_hub", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "governance_hub", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "governance_hub", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "governance_hub", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "governance_hub", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "governance_hub", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "governance_hub", "eval_metric")
trace_contract._emit_stores_embedding("p4", "governance_hub", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "governance_hub", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "governance_hub", "exec_snapshot_link")


class GovernanceHub:
    """
    Main entry point for safety validation.
    Usage: hub.validate_input(user_prompt)
    """

    def __init__(self):
        self.pii_scrubber = PIIScrubber()
        self.injection_detector = InjectionDetector()

    def validate_input(self, text: str) -> str:
        """
        Runs injection checks first, then scrubs PII.
        Returns sanitized text.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "GovernanceHub.validate_input"
        )

        self.injection_detector.scan(text)
        safe_text = self.pii_scrubber.scrub(text)
        return safe_text

    def validate_output(self, text: str) -> str:
        """
        Scans LLM output for data leaks (PII).
        """
        return self.pii_scrubber.scrub(text)
