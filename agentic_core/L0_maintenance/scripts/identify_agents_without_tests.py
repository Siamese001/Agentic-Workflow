#!/usr/bin/env python3
"""
Identify agents without test coverage for improvement.
Prioritize by layer and complexity.
"""
import json
from collections import defaultdict
from pathlib import Path

project_root = Path(__file__).parent.parent

# Load discovery data
with open(project_root / "agent_discovery_full.json", encoding='utf-8') as f:
    agents = json.load(f)

# Filter agents without tests
agents_without_tests = [a for a in agents if not a.get('has_tests', False)]

print(f"\n{'='*70}")
print(f"AGENTS WITHOUT TEST COVERAGE: {len(agents_without_tests)}")
print(f"{'='*70}\n")

# Group by territory
by_territory = defaultdict(list)
for agent in agents_without_tests:
    territory = agent.get('territory', 'Unknown')
    by_territory[territory].append(agent)

# Sort territories by layer priority (L6→L0, then Apps)
layer_priority = {
    'L6_Observability': 1,
    'L5 Safety': 2,
    'L4 State': 3,
    'L3 Orchestration': 4,
    'L2 Execution': 5,
    'L1 Cognition': 6,
    'L0 Maintenance': 7,
    'Apps': 8,
    'Utils': 9
}

def get_priority(territory):
    for key, priority in layer_priority.items():
        if territory.startswith(key):
            return priority
    return 10

sorted_territories = sorted(by_territory.keys(), key=get_priority)

print("Agents without tests by territory:\n")
for territory in sorted_territories:
    agents_list = by_territory[territory]
    print(f"{territory}: {len(agents_list)} agents")
    for agent in agents_list:
        name = agent.get('class_name', 'Unknown')
        path = agent.get('path', 'Unknown')
        cc = agent.get('cyclomatic_complexity', 0)
        print(f"  - {name:40} (CC: {cc:2}, Path: {path})")

# Recommend first batch of 8
print(f"\n{'='*70}")
print("RECOMMENDED FIRST BATCH (8 agents)")
print(f"{'='*70}\n")

# Prioritize:
# 1. Base Agents (critical)
# 2. High-layer agents (L6, L5, L4)
# 3. Lower complexity (easier to test)

base_agents = [a for a in agents_without_tests if 'Base Agent' in a.get('territory', '')]
high_layer = [a for a in agents_without_tests if any(
    a.get('territory', '').startswith(layer)
    for layer in ['L6_Observability', 'L5 Safety', 'L4 State']
) and a not in base_agents]

# Sort by complexity (lower first)
base_agents.sort(key=lambda a: a.get('cyclomatic_complexity', 0))
high_layer.sort(key=lambda a: a.get('cyclomatic_complexity', 0))

# Select first 8
batch1 = (base_agents + high_layer)[:8]

for i, agent in enumerate(batch1, 1):
    name = agent.get('class_name', 'Unknown')
    path = agent.get('path', 'Unknown')
    territory = agent.get('territory', 'Unknown')
    cc = agent.get('cyclomatic_complexity', 0)

    print(f"{i}. {name}")
    print(f"   Territory: {territory}")
    print(f"   Path: {path}")
    print(f"   Complexity: {cc}")
    print(f"   Priority: {'BASE AGENT' if 'Base Agent' in territory else 'High Layer'}")
    print()

print(f"{'='*70}")
print("NEXT STEPS")
print(f"{'='*70}\n")
print("For each agent:")
print("1. Add SubatomicTestingMixin to inheritance")
print("2. OR implement _run_self_tests() method")
print("3. Verify tests work")
print("4. Re-run agent discovery")
