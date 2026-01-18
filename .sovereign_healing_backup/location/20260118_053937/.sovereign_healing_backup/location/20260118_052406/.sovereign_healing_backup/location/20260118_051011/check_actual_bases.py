#!/usr/bin/env python3
"""Check what base_classes are actually stored in discovery JSON."""
import json

with open('agent_discovery_full.json', 'r') as f:
    agents = json.load(f)

print("=" * 80)
print("ACTUAL BASE CLASSES IN DISCOVERY JSON")
print("=" * 80)

# Sample agents from each layer
samples = [
    ('L1', 'BudgetAgent'),
    ('L2', 'CartographerAgent'),
    ('L3', 'WorkflowEngineAgent'),
    ('L4', 'FileManagerAgent'),
    ('L5', 'CompositeGuardrailAgent'),
]

for layer, name in samples:
    agent = next((a for a in agents if a['class_name'] == name), None)
    if agent:
        print(f"\n{name} ({layer}):")
        print(f"  base_classes: {agent.get('base_classes', 'NOT FOUND')}")
        print(f"  proper_base_class: {agent.get('proper_base_class', 'NOT FOUND')}")
    else:
        print(f"\n{name}: NOT FOUND IN DISCOVERY")

# Check how many agents actually have base_classes populated
agents_with_bases = [a for a in agents if a.get('base_classes')]
agents_without_bases = [a for a in agents if not a.get('base_classes')]

print(f"\n" + "=" * 80)
print(f"SUMMARY:")
print(f"  Agents with base_classes: {len(agents_with_bases)}")
print(f"  Agents without base_classes: {len(agents_without_bases)}")

if agents_with_bases:
    print(f"\nSample agent WITH bases:")
    sample = agents_with_bases[0]
    print(f"  {sample['class_name']}: {sample.get('base_classes', [])}")
    print(f"  proper_base_class: {sample.get('proper_base_class')}")

print("\n" + "=" * 80)
