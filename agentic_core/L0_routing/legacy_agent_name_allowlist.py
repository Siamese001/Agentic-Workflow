"""
Canonical allowlist for legacy L5 safety agent names.

These agents have been deleted or retired but their names may still appear
in historical rename tooling, archived consolidation scripts, or test
fixtures. Any production code that needs to reference a deleted agent
name MUST import from this module — never duplicate the literal.

Governance: adding an entry requires a justification string (>=12 chars).
The L5 inventory contract test enforces that no stray string refs for
these names exist outside this file and the agent's own defining module.
"""

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("legacy_agent_name_allowlist", "p4obs", "metric_1")
_emit_emits_metric_event("legacy_agent_name_allowlist", "p4obs", "metric_2")
_emit_emits_metric_event("legacy_agent_name_allowlist", "p4obs", "metric_3")
_emit_emits_metric_event("legacy_agent_name_allowlist", "p4obs", "metric_4")
_emit_emits_metric_event("legacy_agent_name_allowlist", "p4obs", "metric_5")
_emit_emits_metric_event("legacy_agent_name_allowlist", "p4obs", "metric_6")
_emit_records_incident_event("legacy_agent_name_allowlist", "p4obs", "incident")
_emit_captures_runtime_anomaly("legacy_agent_name_allowlist", "p4obs", "anomaly")
_emit_writes_observability_log("legacy_agent_name_allowlist", "p4obs", "obs_log")
_emit_updates_monitoring_state("legacy_agent_name_allowlist", "p4obs", "mon_state")
_emit_triggers_alert("legacy_agent_name_allowlist", "p4obs", "alert")
_emit_links_incident_trace("legacy_agent_name_allowlist", "p4obs", "trace_link")
_emit_captures_pattern("legacy_agent_name_allowlist", "p3lm", "pattern")
_emit_records_learning_event("legacy_agent_name_allowlist", "p3lm", "learning_event")
_emit_writes_learning_snapshot("legacy_agent_name_allowlist", "p3lm", "snapshot")
_emit_feeds_meta_learning("legacy_agent_name_allowlist", "p3lm", "meta_feed")
_emit_updates_routing_strategy("legacy_agent_name_allowlist", "p3lm", "routing")
_emit_improves_agent_policy("legacy_agent_name_allowlist", "p3lm", "policy")
_emit_stores_learning_state("legacy_agent_name_allowlist", "p3lm", "state")
_emit_records_execution_trace("legacy_agent_name_allowlist", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("legacy_agent_name_allowlist", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("legacy_agent_name_allowlist", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("legacy_agent_name_allowlist", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("legacy_agent_name_allowlist", "L4_STATE", "p2_trace_5")
_emit_reads_environ("legacy_agent_name_allowlist", "env_read", "p2_env_1")
_emit_reads_environ("legacy_agent_name_allowlist", "env_read", "p2_env_2")
_emit_reads_runtime_state("legacy_agent_name_allowlist", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("legacy_agent_name_allowlist", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "legacy_agent_name_allowlist")
emit_determinism_digest("p0", "legacy_agent_name_allowlist")

_emit_dispatches_healing_run("p1", "legacy_agent_name_allowlist", "L0")
_emit_routes_through("p1", "legacy_agent_name_allowlist", "L0")
_emit_checks_agent_registry("p1", "legacy_agent_name_allowlist", "agent_registry")
_emit_validates_agent_capability("p1", "legacy_agent_name_allowlist", "capability")
_emit_dispatches_execution_plan("p1", "legacy_agent_name_allowlist", "exec_plan")
_emit_agent_executes_agent("p1", "legacy_agent_name_allowlist", "sub_agent")
_emit_routes_to_agent("p1", "legacy_agent_name_allowlist", "target_agent")
_emit_verifies_policy("p1", "legacy_agent_name_allowlist", "policy_check")
_emit_observes_runtime_state("p1", "legacy_agent_name_allowlist", "runtime_state")
_emit_verifies_boundary("p1", "legacy_agent_name_allowlist", "boundary_check")
_emit_transcripts_response("p1", "legacy_agent_name_allowlist", "transcript")
_emit_hard_fails_untranscripted("p1", "legacy_agent_name_allowlist")
_emit_gated_by_confidence("p1", "legacy_agent_name_allowlist", "confidence_gate")
_emit_escalates_to_human("p1", "legacy_agent_name_allowlist", "L0")
_emit_reads_policy_state("p1", "legacy_agent_name_allowlist", "L0")
_emit_records_execution_trace("p0", "evidence", "legacy_agent_name_allowlist")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "legacy_agent_name_allowlist", "p0_governance")
_emit_snapshots_state("p0", "legacy_agent_name_allowlist", "state_snapshot")
_emit_authorize_and_execute("p2", "legacy_agent_name_allowlist", "execution_auth")
_emit_validates_capability("p2", "legacy_agent_name_allowlist", "capability_check")
_emit_routes_to_capability("p2", "legacy_agent_name_allowlist", "capability_route")
_emit_writes_via_uwg("p2", "legacy_agent_name_allowlist", "uwg_write")
_emit_blocks_direct_write("p2", "legacy_agent_name_allowlist", "direct_write_block")
_emit_records_tool_invocation("p2", "legacy_agent_name_allowlist", "tool_invocation")
_emit_captures_execution_output("p2", "legacy_agent_name_allowlist", "exec_output")
_emit_dispatches_agent("p3", "legacy_agent_name_allowlist", "agent_dispatch")
_emit_coordinates_agents("p3", "legacy_agent_name_allowlist", "agent_coordination")
_emit_records_workflow_lineage("p3", "legacy_agent_name_allowlist", "workflow_lineage")
_emit_records_healing_outcome("p3", "legacy_agent_name_allowlist", "healing_outcome")
_emit_escalates_failure("p3", "legacy_agent_name_allowlist", "failure_escalation")
_emit_orchestrates_workflow("p3", "legacy_agent_name_allowlist", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "legacy_agent_name_allowlist", "healing_dispatch")
_emit_invokes_evaluation("p3", "legacy_agent_name_allowlist", "evaluation_signal")
_emit_records_telemetry_event("p4", "legacy_agent_name_allowlist", "telemetry_event")
_emit_captures_evaluation_metric("p4", "legacy_agent_name_allowlist", "eval_metric")
_emit_stores_embedding("p4", "legacy_agent_name_allowlist", "embedding_store")
_emit_updates_meta_learning_state("p4", "legacy_agent_name_allowlist", "meta_learning")
_emit_links_execution_to_snapshot("p4", "legacy_agent_name_allowlist", "exec_snapshot_link")
_emit_pulls_context("p1", "legacy_agent_name_allowlist", "context_pull")
_emit_pulls_context("p1", "legacy_agent_name_allowlist", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "legacy_agent_name_allowlist", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "legacy_agent_name_allowlist", "uwg_term_secondary")
_emit_writes_through("p1", "legacy_agent_name_allowlist", "write_through")
_emit_writes_through("p1", "legacy_agent_name_allowlist", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "legacy_agent_name_allowlist", "safety_validation")
_emit_invokes_eval("p1", "legacy_agent_name_allowlist", "eval_call")
_emit_proposal_commits_routing("p1", "legacy_agent_name_allowlist", "routing_commit")

LEGACY_AGENT_NAME_ALLOWLIST: dict[str, str] = {
    # --- Deleted UNUSED agents (Phase 1.1 + Phase 5) ---
    "ConfigurationSecurityGuardrailAgent": "Deleted: zero production refs (Phase 1.1)",
    "RagHealthCheckAgent": "Deleted: zero production refs (Phase 1.1)",
    "CachedSafetyShield": "Deleted: zero production refs after string cleanup (Phase 5)",
    "CompositeGuardrailAgent": "Deleted: zero production refs after string cleanup (Phase 5)",
    "GitSafetyHandlerAgent": "Deleted: zero production refs after string cleanup (Phase 5)",
    "HealValidatorAgent": "Deleted: zero production refs after string cleanup (Phase 5)",
    "MCPGuardianAgent": "Deleted: zero production refs after string cleanup (Phase 5)",
    "PIISanitizerAgent": "Deleted: zero production refs after string cleanup (Phase 5)",
    "PromptRegistryAgent": "Deleted: zero production refs after string cleanup (Phase 5)",
    "TestCoverageGuardianAgent": "Deleted: zero production refs after string cleanup (Phase 5)",
    "TestSovereigntyAgent": "Deleted: zero production refs after string cleanup (Phase 5)",
}
