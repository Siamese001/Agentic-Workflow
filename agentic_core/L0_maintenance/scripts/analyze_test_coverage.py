#!/usr/bin/env python3
"""Analyze test coverage and identify agents without tests."""
import json
from pathlib import Path

# Load agent discovery data
with open('agent_discovery_full.json', 'r') as f:
    data = json.load(f)

# Handle both list format and dict format
if isinstance(data, list):
    agents = data
else:
    agents = data.get('agents', [])
print(f"Total agents: {len(agents)}")

# Find agents without tests
agents_without_tests = [a for a in agents if not a.get('has_tests', False)]
agents_with_tests = [a for a in agents if a.get('has_tests', False)]

print(f"Agents WITH tests: {len(agents_with_tests)}")
print(f"Agents WITHOUT tests: {len(agents_without_tests)}")
print(f"Current test coverage: {len(agents_with_tests)/len(agents)*100:.1f}%")

print("\n" + "=" * 70)
print("AGENTS NEEDING TESTS:")
print("=" * 70)

# Group by territory
by_territory = {}
for agent in agents_without_tests:
    territory = agent.get('territory', 'Unknown')
    if territory not in by_territory:
        by_territory[territory] = []
    by_territory[territory].append(agent)

for territory in sorted(by_territory.keys()):
    agents_list = by_territory[territory]
    print(f"\n{territory} ({len(agents_list)} agents):")
    for agent in agents_list:
        path = agent.get('path', 'unknown')
        print(f"  - {agent['class_name']}")
        print(f"    Path: {path}")
