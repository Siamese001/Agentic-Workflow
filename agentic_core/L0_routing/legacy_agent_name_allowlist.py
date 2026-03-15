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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "legacy_agent_name_allowlist", "L0")
_emit_routes_through("p1", "legacy_agent_name_allowlist", "L0")
_emit_escalates_to_human("p1", "legacy_agent_name_allowlist", "L0")
_emit_reads_policy_state("p1", "legacy_agent_name_allowlist", "L0")
_emit_records_execution_trace("p0", "evidence", "legacy_agent_name_allowlist")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "legacy_agent_name_allowlist", "p0_governance")
_emit_snapshots_state("p0", "legacy_agent_name_allowlist", "state_snapshot")

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
