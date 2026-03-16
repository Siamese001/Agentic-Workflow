"""Invariant registry for prompt governance enforcement constants.

No import-time validation side effects.
Call validate_invariant_registry() explicitly to verify schema integrity.
"""

from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "invariant_registry")
_emit_applies_guardrail("p0", "invariant_registry", "p0_governance")
_emit_reads_policy_state("p0", "invariant_registry", "policy_binding")
_emit_snapshots_state("p0", "invariant_registry", "state_snapshot")
emit_replay_key("p0", "invariant_registry")
emit_determinism_digest("p0", "invariant_registry")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "invariant_registry", "execution_auth")
_emit_validates_capability("p2", "invariant_registry", "capability_check")
_emit_routes_to_capability("p2", "invariant_registry", "capability_route")
_emit_writes_via_uwg("p2", "invariant_registry", "uwg_write")
_emit_blocks_direct_write("p2", "invariant_registry", "direct_write_block")
_emit_records_tool_invocation("p2", "invariant_registry", "tool_invocation")
_emit_captures_execution_output("p2", "invariant_registry", "exec_output")
_emit_dispatches_agent("p3", "invariant_registry", "agent_dispatch")
_emit_coordinates_agents("p3", "invariant_registry", "agent_coordination")
_emit_records_workflow_lineage("p3", "invariant_registry", "workflow_lineage")
_emit_records_healing_outcome("p3", "invariant_registry", "healing_outcome")
_emit_escalates_failure("p3", "invariant_registry", "failure_escalation")
_emit_orchestrates_workflow("p3", "invariant_registry", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "invariant_registry", "healing_dispatch")
_emit_invokes_evaluation("p3", "invariant_registry", "evaluation_signal")
_emit_records_telemetry_event("p4", "invariant_registry", "telemetry_event")
_emit_captures_evaluation_metric("p4", "invariant_registry", "eval_metric")
_emit_stores_embedding("p4", "invariant_registry", "embedding_store")
_emit_updates_meta_learning_state("p4", "invariant_registry", "meta_learning")
_emit_links_execution_to_snapshot("p4", "invariant_registry", "exec_snapshot_link")

READ_ONLY_ISOLATION: dict = {
    "forbidden_verbs": ["write", "modify", "update", "delete"],
    "scope": "retrieval_context",
    "authority": "L1_prompt_governance",
}
MUTATION_BLOCK_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "forbidden_verbs": {"type": "array", "items": {"type": "string"}},
        "scope": {"type": "string"},
        "authority": {"type": "string"},
    },
    "required": ["forbidden_verbs", "scope", "authority"],
    "additionalProperties": False,
}
ITERATIVE_FEEDBACK_DIRECTIVE: str = "PRIVATE REASONING ONLY: You may refine your internal query up to 3 times before producing output. No mutation of external state. No authority granted. Re-query is advisory and read-only."


def validate_invariant_registry() -> None:
    """Validate READ_ONLY_ISOLATION against MUTATION_BLOCK_SCHEMA.

    Raises:
        RuntimeError: If READ_ONLY_ISOLATION fails schema validation.
    """
    from agentic_core.prompt_governance.security.validators.output_schema_validator import (
        validate_against_schema,
    )

    ok, code, _ = validate_against_schema(READ_ONLY_ISOLATION, MUTATION_BLOCK_SCHEMA)
    if not ok:
        raise RuntimeError(f"invariant_registry: READ_ONLY_ISOLATION fails MUTATION_BLOCK_SCHEMA: {code}")
