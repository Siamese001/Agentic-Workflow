#!/usr/bin/env python3
"""Extract layer statistics from agent discovery JSON."""
import json

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
)

with open(AGENT_DISCOVERY_JSON) as f:
    data = json.load(f)

layers = {'L0': [], 'L1': [], 'L2': [], 'L3': [], 'L4': [], 'L5': []}

for agent in data if isinstance(data, list) else data.get('agents', []):
    layer = agent.get('layer', '')
    if layer in layers:
        layers[layer].append(agent)

print("| Layer | Agents | Testing% | Healing% | MCP% |")
print("|-------|--------|----------|----------|------|")

for layer in ['L0', 'L1', 'L2', 'L3', 'L4', 'L5']:
    agents = layers[layer]
    count = len(agents)
    if count == 0:
        print(f"| {layer} | 0 | 0% | 0% | 0% |")
        continue

    testing = sum(1 for a in agents if a.get('has_tests', False))
    healing = sum(1 for a in agents if a.get('has_healing', False))
    mcp = sum(1 for a in agents if a.get('has_mcp_hardening', False))

    print(f"| {layer} | {count} | {testing*100//count}% | {healing*100//count}% | {mcp*100//count}% |")
