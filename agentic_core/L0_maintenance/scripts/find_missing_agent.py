#!/usr/bin/env python3
"""Find which agent is missing from dashboard territories."""
import json
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DISCOVERY_PATH = PROJECT_ROOT / 'agent_discovery_full.json'

with open(DISCOVERY_PATH, encoding='utf-8') as f:
    agents = json.load(f)

# Group by territory
territory_counts = defaultdict(int)
for agent in agents:
    territory = agent.get('territory', 'Unknown')
    territory_counts[territory] += 1

print("Territory counts from discovery:")
for t, count in sorted(territory_counts.items()):
    print(f"  {t}: {count}")

print(f"\nTotal: {sum(territory_counts.values())}")
