import re

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

_emit_applies_guardrail("p0", "pii_scrubber", "p0_governance")
_emit_reads_policy_state("p0", "pii_scrubber", "policy_binding")
_emit_snapshots_state("p0", "pii_scrubber", "state_snapshot")
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
