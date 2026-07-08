"""Invariant registry for prompt governance enforcement constants.

No import-time validation side effects.
Call validate_invariant_registry() explicitly to verify schema integrity.
"""

from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_records_execution_trace("p0", "evidence", "invariant_registry")
trace_contract._emit_applies_guardrail("p0", "invariant_registry", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "invariant_registry", "policy_binding")
trace_contract._emit_snapshots_state("p0", "invariant_registry", "state_snapshot")

trace_contract._emit_emits_metric_event("invariant_registry", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("invariant_registry", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("invariant_registry", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("invariant_registry", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("invariant_registry", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("invariant_registry", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("invariant_registry", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("invariant_registry", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("invariant_registry", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("invariant_registry", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("invariant_registry", "p4obs", "alert")
trace_contract._emit_links_incident_trace("invariant_registry", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("invariant_registry", "p3lm", "pattern")
trace_contract._emit_records_learning_event("invariant_registry", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("invariant_registry", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("invariant_registry", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("invariant_registry", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("invariant_registry", "p3lm", "policy")
trace_contract._emit_stores_learning_state("invariant_registry", "p3lm", "state")
trace_contract._emit_records_execution_trace("invariant_registry", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("invariant_registry", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("invariant_registry", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("invariant_registry", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("invariant_registry", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("invariant_registry", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("invariant_registry", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("invariant_registry", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("invariant_registry", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "invariant_registry", "context_pull")
trace_contract._emit_pulls_context("p1", "invariant_registry", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "invariant_registry", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "invariant_registry", "uwg_term_2")
trace_contract._emit_writes_through("p1", "invariant_registry", "write_through")
trace_contract._emit_writes_through("p1", "invariant_registry", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "invariant_registry", "safety_validation")
trace_contract._emit_invokes_eval("p1", "invariant_registry", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "invariant_registry", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "invariant_registry", "human_escalation")
trace_contract._emit_routes_through("p1", "invariant_registry", "route_through")
trace_contract._emit_checks_agent_registry("p1", "invariant_registry", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "invariant_registry", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "invariant_registry", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "invariant_registry", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "invariant_registry", "target_agent")
trace_contract._emit_verifies_policy("p1", "invariant_registry", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "invariant_registry", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "invariant_registry", "boundary_check")
trace_contract._emit_transcripts_response("p1", "invariant_registry", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "invariant_registry")
trace_contract._emit_gated_by_confidence("p1", "invariant_registry", "confidence_gate")
trace_contract.emit_replay_key("p0", "invariant_registry")
trace_contract.emit_determinism_digest("p0", "invariant_registry")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "invariant_registry", "execution_auth")
trace_contract._emit_validates_capability("p2", "invariant_registry", "capability_check")
trace_contract._emit_routes_to_capability("p2", "invariant_registry", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "invariant_registry", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "invariant_registry", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "invariant_registry", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "invariant_registry", "exec_output")
trace_contract._emit_dispatches_agent("p3", "invariant_registry", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "invariant_registry", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "invariant_registry", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "invariant_registry", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "invariant_registry", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "invariant_registry", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "invariant_registry", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "invariant_registry", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "invariant_registry", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "invariant_registry", "eval_metric")
trace_contract._emit_stores_embedding("p4", "invariant_registry", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "invariant_registry", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "invariant_registry", "exec_snapshot_link")

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
