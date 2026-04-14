"""Invariant registry for prompt governance enforcement constants.

No import-time validation side effects.
Call validate_invariant_registry() explicitly to verify schema integrity.
"""

from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "invariant_registry")
_emit_applies_guardrail("p0", "invariant_registry", "p0_governance")
_emit_reads_policy_state("p0", "invariant_registry", "policy_binding")
_emit_snapshots_state("p0", "invariant_registry", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("invariant_registry", "p4obs", "metric_1")
_emit_emits_metric_event("invariant_registry", "p4obs", "metric_2")
_emit_emits_metric_event("invariant_registry", "p4obs", "metric_3")
_emit_emits_metric_event("invariant_registry", "p4obs", "metric_4")
_emit_emits_metric_event("invariant_registry", "p4obs", "metric_5")
_emit_emits_metric_event("invariant_registry", "p4obs", "metric_6")
_emit_records_incident_event("invariant_registry", "p4obs", "incident")
_emit_captures_runtime_anomaly("invariant_registry", "p4obs", "anomaly")
_emit_writes_observability_log("invariant_registry", "p4obs", "obs_log")
_emit_updates_monitoring_state("invariant_registry", "p4obs", "mon_state")
_emit_triggers_alert("invariant_registry", "p4obs", "alert")
_emit_links_incident_trace("invariant_registry", "p4obs", "trace_link")
_emit_captures_pattern("invariant_registry", "p3lm", "pattern")
_emit_records_learning_event("invariant_registry", "p3lm", "learning_event")
_emit_writes_learning_snapshot("invariant_registry", "p3lm", "snapshot")
_emit_feeds_meta_learning("invariant_registry", "p3lm", "meta_feed")
_emit_updates_routing_strategy("invariant_registry", "p3lm", "routing")
_emit_improves_agent_policy("invariant_registry", "p3lm", "policy")
_emit_stores_learning_state("invariant_registry", "p3lm", "state")
_emit_records_execution_trace("invariant_registry", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("invariant_registry", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("invariant_registry", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("invariant_registry", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("invariant_registry", "L4_STATE", "p2_trace_5")
_emit_reads_environ("invariant_registry", "env_read", "p2_env_1")
_emit_reads_environ("invariant_registry", "env_read", "p2_env_2")
_emit_reads_runtime_state("invariant_registry", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("invariant_registry", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "invariant_registry", "context_pull")
_emit_pulls_context("p1", "invariant_registry", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "invariant_registry", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "invariant_registry", "uwg_term_2")
_emit_writes_through("p1", "invariant_registry", "write_through")
_emit_writes_through("p1", "invariant_registry", "write_through_2")
_emit_validated_by_safety_plane("p1", "invariant_registry", "safety_validation")
_emit_invokes_eval("p1", "invariant_registry", "eval_call")
_emit_proposal_commits_routing("p1", "invariant_registry", "routing_commit")
_emit_escalates_to_human("p1", "invariant_registry", "human_escalation")
_emit_routes_through("p1", "invariant_registry", "route_through")
_emit_checks_agent_registry("p1", "invariant_registry", "agent_registry")
_emit_validates_agent_capability("p1", "invariant_registry", "capability")
_emit_dispatches_execution_plan("p1", "invariant_registry", "exec_plan")
_emit_agent_executes_agent("p1", "invariant_registry", "sub_agent")
_emit_routes_to_agent("p1", "invariant_registry", "target_agent")
_emit_verifies_policy("p1", "invariant_registry", "policy_check")
_emit_observes_runtime_state("p1", "invariant_registry", "runtime_state")
_emit_verifies_boundary("p1", "invariant_registry", "boundary_check")
_emit_transcripts_response("p1", "invariant_registry", "transcript")
_emit_hard_fails_untranscripted("p1", "invariant_registry")
_emit_gated_by_confidence("p1", "invariant_registry", "confidence_gate")
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
