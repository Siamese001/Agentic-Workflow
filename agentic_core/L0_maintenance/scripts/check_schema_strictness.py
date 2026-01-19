#!/usr/bin/env python3
"""Check schema strictness values for all agents."""
import json
from pathlib import Path
from collections import Counter
from archives.location_violations.file_utils import safe_read_file, safe_write_file

PROJECT_ROOT = Path(__file__).parent.parent

with open(PROJECT_ROOT / 'agent_discovery_full.json', 'r', encoding='utf-8') as f:
    agents = json.load(f)

# Count schema strictness values
strictness_values = Counter()
low_strictness = []

for agent in agents:
    ss = agent.get('schema_strictness', 0)
    strictness_values[ss] += 1
    if ss < 100:
        low_strictness.append({
            'name': agent['class_name'],
            'path': agent['path'],
            'schema_strictness': ss
        })

print(f"Total agents: {len(agents)}")
print(f"\nSchema Strictness distribution:")
for value, count in sorted(strictness_values.items()):
    print(f"  {value}%: {count} agents")

print(f"\nAgents with Schema Strictness < 100%: {len(low_strictness)}")
print("\nFirst 20 agents needing schema fixes:")
for agent in low_strictness[:20]:
    print(f"  {agent['name']}: {agent['schema_strictness']}% - {agent['path']}")
