#!/usr/bin/env python3
"""Identify duplicate agent names and their locations."""
import json
from pathlib import Path

discovery_file = Path("agent_discovery_full.json")
data = json.loads(discovery_file.read_text())

# Group by class name
from collections import defaultdict
by_name = defaultdict(list)
for agent in data:
    by_name[agent['class_name']].append(agent)

# Find duplicates
duplicates = {name: agents for name, agents in by_name.items() if len(agents) > 1}

print(f"Found {len(duplicates)} duplicate agent names:\n")
for name, agents in sorted(duplicates.items()):
    print(f"\n{name} ({len(agents)} instances):")
    for agent in agents:
        location = agent['path']
        layer = agent.get('layer', 'Unknown')
        print(f"  [{layer:8s}] {location}")
