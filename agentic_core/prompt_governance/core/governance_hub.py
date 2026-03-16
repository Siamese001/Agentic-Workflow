
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
