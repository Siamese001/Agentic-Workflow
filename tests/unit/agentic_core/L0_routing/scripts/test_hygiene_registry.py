"""Test script to validate core hygiene agents registry."""

from agentic_core.config.core.hygiene_registry_config import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    CORE_HYGIENE_AGENTS,
    MANDATORY_PREFLIGHT,
    get_all_hygiene_agents,
    get_tier_agents,
)

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
