"""
[DEPRECATED] Analyze agent_discovery_full.json

Use scripts/full_agent_discovery.py as the canonical AST scan.
This script just reads the JSON output - run full_agent_discovery.py first.
"""
import json
from collections import defaultdict

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)

with open(AGENT_DISCOVERY_JSON, 'r') as f:
    data = json.load(f)

print(f"Total entries: {len(data)}")

layers = defaultdict(int)
for a in data:
    layers[a.get('layer', 'unknown')] += 1

print("\nBy layer:")
for layer, count in sorted(layers.items()):
    print(f"  {layer}: {count}")

# Core layers (L0-L5)
core_count = sum(layers.get(f'L{i}', 0) for i in range(6))
print(f"\nCore (L0-L5): {core_count}")

# Healing coverage
healing_count = sum(1 for a in data if a.get('has_healing', False))
print(f"Has healing: {healing_count}")
print(f"Healing %: {100 * healing_count // len(data)}%")
