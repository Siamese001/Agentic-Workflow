#!/usr/bin/env python3
"""Check actual healing capability in agent_discovery_full.json"""
import json
from pathlib import Path

data = json.load(open('agent_discovery_full.json'))
print(f"Total agents: {len(data)}")

has_healing = [a for a in data if a.get('has_healing')]
no_healing = [a for a in data if not a.get('has_healing')]

print(f"Has healing: {len(has_healing)}")
print(f"NO healing: {len(no_healing)}")
print(f"Heal Cap %: {len(has_healing)/len(data)*100:.1f}%")

if no_healing:
    print(f"\nAgents WITHOUT healing ({len(no_healing)}):")
    for a in no_healing[:20]:
        print(f"  - {a['class_name']}: {a['path']}")
