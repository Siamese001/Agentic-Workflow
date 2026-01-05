#!/usr/bin/env python3
"""Quick check of L4 agent count in dashboard"""
from pathlib import Path
import json

# Check discovery JSON
data = json.load(open('agent_discovery_full.json'))
l4_agents = [a for a in data if a['layer'] == 'L4']
print(f"L4 agents in agent_discovery_full.json: {len(l4_agents)}")

# Check dashboard HTML
html = Path('reports/autonomy_dashboard.html').read_text(encoding='utf-8')
data_start = html.find('const dashboardData = ')
data_end = html.find('];', data_start)
data_str = html[data_start+22:data_end+1]
dashboard_data = json.loads(data_str)

l4_rows = [r for r in dashboard_data if 'L4' in r.get('Territory', '')]
print(f"\nL4 State rows in dashboard HTML: {len(l4_rows)}")
for r in l4_rows:
    print(f"  {r['Territory']}: {r['Total']} agents")

# Check total
total_row = [r for r in dashboard_data if r.get('Territory') == 'TOTAL']
if total_row:
    print(f"\nTotal agents in dashboard: {total_row[0]['Total']}")
