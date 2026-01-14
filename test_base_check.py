#!/usr/bin/env python3
"""Test to understand why proper_base_class is False for all agents."""
import json

with open('agent_discovery_full.json', 'r') as f:
    agents = json.load(f)

# Sample agents that SHOULD have proper base
test_agents = [
    'L1CognitionBaseAgent',
    'L2Agent', 
    'L3Agent',
    'L4Agent',
    'L5Agent',
    'L6Agent',
    'L5SafetyBaseAgent',
    'L3OrchestrationBaseAgent',
    'L2ExecutionBaseAgent'
]

print("=" * 80)
print("BASE CLASS CHECK DEBUG")
print("=" * 80)

for name in test_agents:
    agent = next((a for a in agents if a['class_name'] == name), None)
    if agent:
        print(f"\n{name}:")
        print(f"  proper_base_class: {agent.get('proper_base_class', 'NOT FOUND')}")
        print(f"  base_classes: {agent.get('base_classes', [])}")
        print(f"  layer: {agent.get('layer', 'Unknown')}")
        print(f"  territory: {agent.get('territory', 'Unknown')}")
    else:
        print(f"\n{name}: NOT FOUND")

# Check a few regular agents that inherit from layer bases
print("\n" + "=" * 80)
print("SAMPLE REGULAR AGENTS")
print("=" * 80)

regular_samples = [a for a in agents if a.get('layer') == 'L1'][:5]
for agent in regular_samples:
    print(f"\n{agent['class_name']}:")
    print(f"  proper_base_class: {agent.get('proper_base_class', 'NOT FOUND')}")
    print(f"  base_classes: {agent.get('base_classes', [])}")

print("\n" + "=" * 80)
