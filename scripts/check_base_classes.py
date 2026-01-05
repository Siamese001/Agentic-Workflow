#!/usr/bin/env python3
"""Check where base class agents are counted in territory summary"""
from pathlib import Path
import json

html = Path('reports/autonomy_dashboard.html').read_text(encoding='utf-8')

# Extract dashboardData JSON
start = html.find('const dashboardData = ') + 22
end = html.find('];', start) + 1
data = json.loads(html[start:end])

print("Territories with 'Base' in name:")
print("=" * 60)
for r in data:
    territory = r.get('Territory', 'N/A')
    if 'Base' in territory:
        print(f"  {territory}: {r.get('Total', 0)} agents")

print("\n" + "=" * 60)
print("Looking for base class agents in all territories:")
print("=" * 60)

base_class_patterns = ['BaseAgent', 'Base', 'CanonBaseAgent']
base_agents_found = []

for r in data:
    territory = r.get('Territory', 'N/A')
    if territory == 'TOTAL':
        continue
    agents = r.get('agents', [])
    for agent in agents:
        rel = agent.get('rel', '')
        class_name = agent.get('class_name', '')
        # Check if this looks like a base class
        if any(p in class_name for p in base_class_patterns) or 'base' in rel.lower():
            base_agents_found.append({
                'territory': territory,
                'rel': rel,
                'class_name': class_name
            })

print(f"\nFound {len(base_agents_found)} potential base class agents:")
for agent in base_agents_found:
    print(f"  {agent['territory']:40} | {agent['class_name'] or agent['rel']}")
