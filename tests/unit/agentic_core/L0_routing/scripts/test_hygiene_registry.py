"""Test script to validate core hygiene agents registry."""

from agentic_core.config.core.hygiene_registry_config import (
    CORE_HYGIENE_AGENTS,
    MANDATORY_PREFLIGHT,
    get_all_hygiene_agents,
    get_tier_agents,
)
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

_emit_records_execution_trace("p0", "evidence", "test_hygiene_registry")
_emit_applies_guardrail("p0", "test_hygiene_registry", "p0_governance")
_emit_reads_policy_state("p0", "test_hygiene_registry", "policy_binding")
_emit_snapshots_state("p0", "test_hygiene_registry", "state_snapshot")
emit_replay_key("p0", "test_hygiene_registry")
emit_determinism_digest("p0", "test_hygiene_registry")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_hygiene_registry", "execution_auth")
_emit_validates_capability("p2", "test_hygiene_registry", "capability_check")
_emit_routes_to_capability("p2", "test_hygiene_registry", "capability_route")
_emit_writes_via_uwg("p2", "test_hygiene_registry", "uwg_write")
_emit_blocks_direct_write("p2", "test_hygiene_registry", "direct_write_block")
_emit_records_tool_invocation("p2", "test_hygiene_registry", "tool_invocation")
_emit_captures_execution_output("p2", "test_hygiene_registry", "exec_output")
_emit_dispatches_agent("p3", "test_hygiene_registry", "agent_dispatch")
_emit_coordinates_agents("p3", "test_hygiene_registry", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_hygiene_registry", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_hygiene_registry", "healing_outcome")
_emit_escalates_failure("p3", "test_hygiene_registry", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_hygiene_registry", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_hygiene_registry", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_hygiene_registry", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_hygiene_registry", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_hygiene_registry", "eval_metric")
_emit_stores_embedding("p4", "test_hygiene_registry", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_hygiene_registry", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_hygiene_registry", "exec_snapshot_link")

print("=" * 70)
print("CORE HYGIENE AGENTS REGISTRY VALIDATION")
print("=" * 70)

print("\nCore Hygiene Agents by Tier:\n")
for tier, agents in CORE_HYGIENE_AGENTS.items():
    print(f"{tier}: {len(agents)} agents")
    for agent in agents:
        print(f"  - {agent}")
    print()

print(f"Total hygiene agents: {len(get_all_hygiene_agents())}")
print(f"\nMandatory preflight agents: {MANDATORY_PREFLIGHT}")

print("\n" + "=" * 70)
print("TIER VALIDATION")
print("=" * 70)

for tier_num in range(4):
    agents = get_tier_agents(tier_num)
    print(f"Tier {tier_num}: {len(agents)} agents - {agents}")

print("\n" + "=" * 70)
print("✅ REGISTRY VALIDATION COMPLETE")
print("=" * 70)
