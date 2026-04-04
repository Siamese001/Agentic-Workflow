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

_emit_records_execution_trace("p0", "evidence", "legacy_agent_name_allowlist")
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
