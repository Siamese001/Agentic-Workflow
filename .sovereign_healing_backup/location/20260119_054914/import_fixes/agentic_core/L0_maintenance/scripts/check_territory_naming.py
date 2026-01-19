#!/usr/bin/env python3
"""Check territory naming in agent_discovery_full.json"""
import json
from pathlib import Path
from collections import defaultdict
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

project_root = Path(__file__).parent.parent

# Load agent discovery
with open(project_root / "agent_discovery_full.json") as f:
    agents = json.load(f)

# Find SovereignBaseAgent
sovereign = [a for a in agents if a['class_name'] == 'SovereignBaseAgent']
if sovereign:
    print(f"SovereignBaseAgent territory: '{sovereign[0]['territory']}'")
else:
    print("SovereignBaseAgent NOT FOUND")

# Find all Base Agent territories
print("\nAll Base Agent territories:")
base_agents = [a for a in agents if 'Base Agent' in a.get('territory', '')]
for a in base_agents[:15]:
    print(f"  {a['class_name']:40} -> {a['territory']}")

# Check for Apps territories
print("\nApps territories:")
apps_agents = [a for a in agents if a.get('territory', '').startswith('Apps')]
apps_territories = defaultdict(list)
for a in apps_agents:
    apps_territories[a['territory']].append(a['class_name'])

for territory, agents_list in sorted(apps_territories.items()):
    print(f"  {territory}: {len(agents_list)} agents")
    for agent in agents_list[:3]:
        print(f"    - {agent}")

# Check for Utils territory
print("\nUtils territory:")
utils_agents = [a for a in agents if a.get('territory', '') == 'utils']
print(f"  utils: {len(utils_agents)} agents")
for a in utils_agents[:5]:
    print(f"    - {a['class_name']}")

# Check all unique territories
print("\nAll unique territories:")
territories = defaultdict(int)
for a in agents:
    territories[a.get('territory', 'MISSING')] += 1

for territory, count in sorted(territories.items()):
    print(f"  {territory}: {count} agents")
