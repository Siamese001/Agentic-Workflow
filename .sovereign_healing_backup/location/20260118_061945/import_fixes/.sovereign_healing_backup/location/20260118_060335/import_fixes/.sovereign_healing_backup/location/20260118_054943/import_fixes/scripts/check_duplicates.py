#!/usr/bin/env python3
"""Check for duplicate agents in discovery JSON"""
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

agents = json.load(open(AGENT_DISCOVERY_JSON))

# Check for RegressionOracleAgent specifically
print("RegressionOracleAgent matches:")
for a in agents:
    if 'RegressionOracle' in a.get('class_name', ''):
        print(f"  {a['class_name']} @ {a['path']}")

# Check for all duplicates by class_name
print("\n" + "=" * 60)
print("Checking for duplicate class names:")
by_name = defaultdict(list)
for a in agents:
    by_name[a['class_name']].append(a['path'])

duplicates = {k: v for k, v in by_name.items() if len(v) > 1}
if duplicates:
    print(f"\nFound {len(duplicates)} duplicate class names:")
    for name, paths in sorted(duplicates.items()):
        print(f"\n  {name} ({len(paths)} occurrences):")
        for p in paths:
            print(f"    - {p}")
else:
    print("\nNo duplicate class names found")

# Check for duplicate paths
print("\n" + "=" * 60)
print("Checking for duplicate paths:")
by_path = defaultdict(list)
for a in agents:
    by_path[a['path']].append(a['class_name'])

dup_paths = {k: v for k, v in by_path.items() if len(v) > 1}
if dup_paths:
    print(f"\nFound {len(dup_paths)} paths with multiple classes:")
    for path, names in sorted(dup_paths.items()):
        print(f"\n  {path}:")
        for n in names:
            print(f"    - {n}")
else:
    print("\nNo duplicate paths found")
