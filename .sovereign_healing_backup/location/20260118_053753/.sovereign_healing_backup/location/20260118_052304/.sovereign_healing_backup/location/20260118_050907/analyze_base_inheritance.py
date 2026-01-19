#!/usr/bin/env python3
"""Analyze agents missing proper base class inheritance."""
import json
from collections import defaultdict

with open('agent_discovery_full.json', 'r') as f:
    agents = json.load(f)

print("=" * 80)
print("BASE CLASS INHERITANCE ANALYSIS")
print("=" * 80)

# Find agents missing proper base class
missing_base = [a for a in agents if not a.get('proper_base_class', False)]
has_base = [a for a in agents if a.get('proper_base_class', False)]

print(f"\nTotal agents: {len(agents)}")
print(f"With proper base: {len(has_base)} ({len(has_base)/len(agents)*100:.1f}%)")
print(f"Missing base: {len(missing_base)} ({len(missing_base)/len(agents)*100:.1f}%)")

# Group by layer
by_layer = defaultdict(list)
for agent in missing_base:
    layer = agent.get('layer', 'Unknown')
    by_layer[layer].append(agent['class_name'])

print(f"\nMISSING BASE INHERITANCE BY LAYER:")
for layer in sorted(by_layer.keys()):
    agents_list = by_layer[layer]
    print(f"\n{layer}: {len(agents_list)} agents")
    for name in sorted(agents_list)[:10]:  # Show first 10
        print(f"  - {name}")
    if len(agents_list) > 10:
        print(f"  ... and {len(agents_list) - 10} more")

# Analyze base classes they currently inherit from
print(f"\nCURRENT BASE CLASSES (for agents missing proper base):")
base_class_counts = defaultdict(int)
for agent in missing_base:
    bases = agent.get('inheritance', [])  # Field is 'inheritance' not 'base_classes'
    if bases:
        for base in bases:
            base_class_counts[base] += 1
    else:
        base_class_counts['<none>'] += 1

for base, count in sorted(base_class_counts.items(), key=lambda x: -x[1])[:15]:
    print(f"  {base}: {count} agents")

print("\n" + "=" * 80)
