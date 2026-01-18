"""Debug script to identify invocation pipeline discrepancy."""
import json
from pathlib import Path

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
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

PROJECT_ROOT = Path(__file__).parent.parent

# Load registry
registry = json.load(open(PROJECT_ROOT / AGENT_DISCOVERY_JSON))
print(f"JSON agents: {len(registry)}")

# Create lookup (same logic as dashboard)
registry_by_path = {}
for entry in registry:
    p = (entry.get("path") or "").replace("\\", "/")
    if p:
        registry_by_path[p] = entry

print(f"Registry paths: {len(registry_by_path)}")

# Count invocation from JSON
inv_counts = {}
for entry in registry:
    inv = entry.get('invocation', 'Missing')
    inv_counts[inv] = inv_counts.get(inv, 0) + 1
print(f"JSON invocation counts: {inv_counts}")

# Simulate dashboard agent processing
all_agents = []
for agent in registry:
    path_str = agent.get("path", "")
    if path_str:
        full_path = PROJECT_ROOT / path_str
        if full_path.exists():
            all_agents.append(full_path)

print(f"Resolved agent paths: {len(all_agents)}")

# Simulate lookup as dashboard does
found = 0
not_found = 0
not_found_paths = []
invocation_from_lookup = {"Yes": 0, "No (missing super)": 0, "Inherited": 0}

for agent in all_agents:
    rel_path = str(agent.relative_to(PROJECT_ROOT)).replace("\\", "/")
    entry = registry_by_path.get(rel_path)
    if entry:
        found += 1
        inv = entry.get("invocation", "Inherited")
        invocation_from_lookup[inv] = invocation_from_lookup.get(inv, 0) + 1
    else:
        not_found += 1
        not_found_paths.append(rel_path)

print(f"\nLookup results: found={found}, not_found={not_found}")
if not_found_paths:
    print("Not found paths:")
    for p in not_found_paths[:10]:
        print(f"  {p}")

print(f"Invocation from lookup: {invocation_from_lookup}")

yes = invocation_from_lookup.get("Yes", 0)
inh = invocation_from_lookup.get("Inherited", 0)
no = invocation_from_lookup.get("No (missing super)", 0)
total = yes + inh + no
if total > 0:
    pct = (yes + inh) / total * 100
    print(f"\nExpected Invocation %: {pct:.1f}%")

# Show sample registry paths
print("\nSample registry paths:")
for i, p in enumerate(list(registry_by_path.keys())[:5]):
    print(f"  {p}")

# Show sample agent paths  
print("\nSample agent rel_paths:")
for i, a in enumerate(all_agents[:5]):
    print(f"  {str(a.relative_to(PROJECT_ROOT)).replace(chr(92), '/')}")
