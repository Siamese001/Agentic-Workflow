#!/usr/bin/env python3
"""Find the remaining agents missing heal_repository."""
import json

# Load agent discovery
with open('C:/Git/Agentic-Workflow/agent_discovery_full.json', encoding='utf-8') as f:
    data = json.load(f)

# Find agents missing heal_repository
missing = [a for a in data if not a.get('has_healing')]
print(f"Agents missing healing: {len(missing)}")

for agent in missing:
    print(f"  {agent['path']}")
