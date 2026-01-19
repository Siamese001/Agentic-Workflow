#!/usr/bin/env python3
"""Check which territories have per-agent drill-down data"""
from pathlib import Path
import json

html = Path('reports/autonomy_dashboard.html').read_text(encoding='utf-8')

# Extract dashboardData JSON
data_start = html.find('const dashboardData = ')
data_end = html.find('];', data_start)
data_str = html[data_start+22:data_end+1]
dashboard_data = json.loads(data_str)

print("Territory Drill-Down Data Check")
print("=" * 70)
print(f"{'Territory':<40} {'Total':>6} {'Agents':>8} {'Status'}")
print("-" * 70)

missing = []
for row in dashboard_data:
    territory = row.get('Territory', 'Unknown')
    total = row.get('Total', 0)
    agents = row.get('agents', [])
    agent_count = len(agents) if agents else 0
    
    if territory == 'TOTAL':
        continue
        
    status = '✅' if agent_count > 0 else '❌ MISSING'
    print(f"{territory:<40} {total:>6} {agent_count:>8} {status}")
    
    if agent_count == 0 and total > 0:
        missing.append(territory)

print("-" * 70)
if missing:
    print(f"\n❌ {len(missing)} territories missing drill-down data:")
    for t in missing:
        print(f"   - {t}")
else:
    print("\n✅ All territories have drill-down data")
