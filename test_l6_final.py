#!/usr/bin/env python3
import json

with open('agent_discovery_full.json', 'r') as f:
    data = json.load(f)

l6_agents = [a for a in data if a.get('layer') == 'L6']
print(f"Total L6 agents: {len(l6_agents)}")

base_agents = [a for a in l6_agents if 'Base' in a.get('territory', '')]
print(f"L6 Base Class agents: {len(base_agents)}")

for agent in l6_agents:
    print(f"  {agent['class_name']} -> {agent.get('territory')}")
