"""Analyze agent_discovery_full.json"""
import json
from collections import defaultdict

with open('agent_discovery_full.json', 'r') as f:
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
