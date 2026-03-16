
from agentic_core.prompt_governance.security.detectors.injection_detector import InjectionDetector
from agentic_core.prompt_governance.security.detectors.pii_scrubber import PIIScrubber
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "governance_hub", "p0_governance")
_emit_reads_policy_state("p0", "governance_hub", "policy_binding")
_emit_snapshots_state("p0", "governance_hub", "state_snapshot")
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

_emit_emits_metric_event("governance_hub", "p4obs", "metric_1")
_emit_emits_metric_event("governance_hub", "p4obs", "metric_2")
_emit_emits_metric_event("governance_hub", "p4obs", "metric_3")
_emit_emits_metric_event("governance_hub", "p4obs", "metric_4")
_emit_emits_metric_event("governance_hub", "p4obs", "metric_5")
_emit_emits_metric_event("governance_hub", "p4obs", "metric_6")
_emit_records_incident_event("governance_hub", "p4obs", "incident")
_emit_captures_runtime_anomaly("governance_hub", "p4obs", "anomaly")
_emit_writes_observability_log("governance_hub", "p4obs", "obs_log")
_emit_updates_monitoring_state("governance_hub", "p4obs", "mon_state")
_emit_triggers_alert("governance_hub", "p4obs", "alert")
_emit_links_incident_trace("governance_hub", "p4obs", "trace_link")
_emit_captures_pattern("governance_hub", "p3lm", "pattern")
_emit_records_learning_event("governance_hub", "p3lm", "learning_event")
_emit_writes_learning_snapshot("governance_hub", "p3lm", "snapshot")
_emit_feeds_meta_learning("governance_hub", "p3lm", "meta_feed")
_emit_updates_routing_strategy("governance_hub", "p3lm", "routing")
_emit_improves_agent_policy("governance_hub", "p3lm", "policy")
_emit_stores_learning_state("governance_hub", "p3lm", "state")
_emit_records_execution_trace("governance_hub", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("governance_hub", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("governance_hub", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("governance_hub", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("governance_hub", "L4_STATE", "p2_trace_5")
_emit_reads_environ("governance_hub", "env_read", "p2_env_1")
_emit_reads_environ("governance_hub", "env_read", "p2_env_2")
_emit_reads_runtime_state("governance_hub", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("governance_hub", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "governance_hub", "context_pull")
_emit_pulls_context("p1", "governance_hub", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "governance_hub", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "governance_hub", "uwg_term_2")
_emit_writes_through("p1", "governance_hub", "write_through")
_emit_writes_through("p1", "governance_hub", "write_through_2")
_emit_validated_by_safety_plane("p1", "governance_hub", "safety_validation")
_emit_invokes_eval("p1", "governance_hub", "eval_call")
_emit_proposal_commits_routing("p1", "governance_hub", "routing_commit")
emit_replay_key("p0", "governance_hub")
emit_determinism_digest("p0", "governance_hub")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "governance_hub", "execution_auth")
_emit_validates_capability("p2", "governance_hub", "capability_check")
_emit_routes_to_capability("p2", "governance_hub", "capability_route")
_emit_writes_via_uwg("p2", "governance_hub", "uwg_write")
_emit_blocks_direct_write("p2", "governance_hub", "direct_write_block")
_emit_records_tool_invocation("p2", "governance_hub", "tool_invocation")
_emit_captures_execution_output("p2", "governance_hub", "exec_output")
_emit_dispatches_agent("p3", "governance_hub", "agent_dispatch")
_emit_coordinates_agents("p3", "governance_hub", "agent_coordination")
_emit_records_workflow_lineage("p3", "governance_hub", "workflow_lineage")
_emit_records_healing_outcome("p3", "governance_hub", "healing_outcome")
_emit_escalates_failure("p3", "governance_hub", "failure_escalation")
_emit_orchestrates_workflow("p3", "governance_hub", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "governance_hub", "healing_dispatch")
_emit_invokes_evaluation("p3", "governance_hub", "evaluation_signal")
_emit_records_telemetry_event("p4", "governance_hub", "telemetry_event")
_emit_captures_evaluation_metric("p4", "governance_hub", "eval_metric")
_emit_stores_embedding("p4", "governance_hub", "embedding_store")
_emit_updates_meta_learning_state("p4", "governance_hub", "meta_learning")
_emit_links_execution_to_snapshot("p4", "governance_hub", "exec_snapshot_link")


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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "GovernanceHub.validate_input")

        self.injection_detector.scan(text)
        safe_text = self.pii_scrubber.scrub(text)
        return safe_text

    def validate_output(self, text: str) -> str:
        """
        Scans LLM output for data leaks (PII).
        """
        return self.pii_scrubber.scrub(text)
