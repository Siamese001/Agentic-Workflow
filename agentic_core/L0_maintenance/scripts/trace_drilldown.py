#!/usr/bin/env python3
"""Trace what territory names are used in onclick handlers"""
from pathlib import Path
import re

html = Path('reports/autonomy_dashboard.html').read_text(encoding='utf-8')

# Find all onclick handlers with openDrillModal
pattern = r"onclick=\"openDrillModal\('([^']+)'(?:,\s*'([^']*)')?\)\""
matches = re.findall(pattern, html)

print("Drill-down onclick handlers found:")
print("=" * 70)
territories_clicked = set()
for territory, sub in matches[:30]:  # First 30
    territories_clicked.add(territory)
    print(f"  Territory: '{territory}' | Sub: '{sub}'")

print("\n" + "=" * 70)
print(f"Unique territories in onclick: {len(territories_clicked)}")

# Now check if these match dashboardData territories
import json
data_start = html.find('const dashboardData = ')
data_end = html.find('];', data_start)
data_str = html[data_start+22:data_end+1]
dashboard_data = json.loads(data_str)

data_territories = {r.get('Territory') for r in dashboard_data if r.get('Territory') != 'TOTAL'}

print(f"Territories in dashboardData: {len(data_territories)}")

# Check for mismatches
onclick_only = territories_clicked - data_territories
data_only = data_territories - territories_clicked

if onclick_only:
    print(f"\n❌ In onclick but NOT in dashboardData:")
    for t in onclick_only:
        print(f"   '{t}'")

if data_only:
    print(f"\n⚠️  In dashboardData but NOT in onclick:")
    for t in data_only:
        print(f"   '{t}'")

if not onclick_only and not data_only:
    print("\n✅ All territory names match!")
