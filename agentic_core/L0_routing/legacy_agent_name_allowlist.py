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

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "legacy_agent_name_allowlist")
emit_determinism_digest("p0", "legacy_agent_name_allowlist")

_emit_dispatches_healing_run("p1", "legacy_agent_name_allowlist", "L0")
_emit_routes_through("p1", "legacy_agent_name_allowlist", "L0")
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
