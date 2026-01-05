#!/usr/bin/env python3
"""Check for duplicate agents in discovery JSON"""
import json
from collections import defaultdict

agents = json.load(open('agent_discovery_full.json'))

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
