#!/usr/bin/env python3
"""Check territory sum vs discovery count."""
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DASHBOARD_PATH = PROJECT_ROOT / 'agentic_core' / 'L6_observability' / 'dashboards' / 'autonomy_dashboard.html'
DISCOVERY_PATH = PROJECT_ROOT / 'agent_discovery_full.json'

# Load discovery
with open(DISCOVERY_PATH, 'r', encoding='utf-8') as f:
    agents = json.load(f)
discovery_count = len(agents)

# Load dashboard
content = DASHBOARD_PATH.read_text(encoding='utf-8')
start_marker = 'const dashboardData = ['
end_marker = '];'
start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx) + len(end_marker)
json_str = content[start_idx + len(start_marker) - 1:end_idx - 1]
territories = json.loads(json_str)

# Calculate sum
total_from_territories = sum(r.get('Total', 0) for r in territories if r.get('Territory') != 'TOTAL')
total_row = [r for r in territories if r.get('Territory') == 'TOTAL'][0]

print(f"Discovery count: {discovery_count}")
print(f"Sum of territory totals: {total_from_territories}")
print(f"TOTAL row value: {total_row.get('Total')}")
print(f"Difference: {total_from_territories - discovery_count}")

# Show each territory
print("\nTerritory breakdown:")
for t in territories:
    if t.get('Territory') != 'TOTAL':
        print(f"  {t.get('Territory')}: {t.get('Total')}")
