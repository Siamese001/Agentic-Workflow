#!/usr/bin/env python3
import json

with open('agent_discovery_full.json', 'r') as f:
    data = json.load(f)

l6_agents = [a for a in data if a.get('layer') == 'L6']
print(f"Total L6 agents: {len(l6_agents)}")

base_agents = [a for a in l6_agents if 'Base' in a.get('territory', '')]
print(f"L6 Base Class agents: {len(base_agents)}")

for agent in base_agents:
    print(f"  {agent['class_name']} -> {agent.get('territory')}")

print("\nAll L6 territories:")
territories = set(a.get('territory', 'NO TERRITORY') for a in l6_agents)
for t in sorted(territories):
    count = len([a for a in l6_agents if a.get('territory') == t])
    print(f"  {t}: {count} agents")
