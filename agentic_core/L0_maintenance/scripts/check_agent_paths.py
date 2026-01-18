#!/usr/bin/env python3
import json
from collections import defaultdict

with open('C:/Git/Agentic-Workflow/agent_discovery_full.json', 'r') as f:
    agents = json.load(f)

# Group by layer
by_layer = defaultdict(list)
for agent in agents:
    layer = agent.get('layer', 'Unknown')
    by_layer[layer].append(agent['path'])

# Print sample paths for each layer
for layer in sorted(by_layer.keys()):
    print(f"\n{layer} ({len(by_layer[layer])} agents):")
    for path in by_layer[layer][:5]:
        print(f"  {path}")
