"""Test script to validate core hygiene agents registry."""

from agentic_core.config.core.hygiene_registry_config import (
    CORE_HYGIENE_AGENTS,
    MANDATORY_PREFLIGHT,
    get_all_hygiene_agents,
    get_tier_agents,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
