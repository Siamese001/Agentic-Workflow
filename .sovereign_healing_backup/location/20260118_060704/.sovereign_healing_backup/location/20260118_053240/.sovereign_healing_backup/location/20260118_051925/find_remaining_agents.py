#!/usr/bin/env python3
"""Identify the 17 agents still missing proper base class inheritance."""
import json

with open('agent_discovery_full.json', 'r') as f:
    agents = json.load(f)

missing = [a for a in agents if not a.get('proper_base_class', False)]

print("=" * 80)
print(f"REMAINING {len(missing)} AGENTS WITHOUT PROPER BASE CLASS")
print("=" * 80)

by_layer = {}
for agent in missing:
    layer = agent.get('layer', 'Unknown')
    if layer not in by_layer:
        by_layer[layer] = []
    by_layer[layer].append(agent)

for layer in sorted(by_layer.keys()):
    agents_list = by_layer[layer]
    print(f"\n{layer}: {len(agents_list)} agents")
    for agent in agents_list:
        bases = agent.get('inheritance', [])
        print(f"  {agent['class_name']}")
        print(f"    Path: {agent['path']}")
        print(f"    Inherits from: {bases if bases else '<NONE>'}")

print("\n" + "=" * 80)
print("ACTION PLAN:")
print("These agents need to inherit from appropriate base classes:")
print("- L1 agents → L1CognitionBaseAgent or SovereignBaseAgent")
print("- L2 agents → L2ExecutionBaseAgent or SovereignBaseAgent")
print("- L3 agents → L3OrchestrationBaseAgent or SovereignBaseAgent")
print("- L4 agents → L4StateBaseAgent or SovereignBaseAgent")
print("=" * 80)
