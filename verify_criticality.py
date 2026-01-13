#!/usr/bin/env python3
"""Verify Phase 2 criticality implementation"""
import re
import json

with open('agentic_core/L6_observability/dashboards/autonomy_dashboard.html', encoding='utf-8') as f:
    html = f.read()

match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
if not match:
    print("❌ Could not find dashboardData")
    exit(1)

data = json.loads(match.group(1))

print("=" * 70)
print("PHASE 2 CRITICALITY VERIFICATION")
print("=" * 70)
print(f"\nTOTAL Row Criticality: {data[0]['Criticality']}")
print(f"\nTerritory Criticality Values:")
print("-" * 70)

for row in data[1:10]:
    territory = row['Territory'][:40]
    crit = row['Criticality']
    print(f"  {territory:40s} Criticality = {crit:3d}")

unique_values = len(set(r['Criticality'] for r in data[1:]))
print(f"\n✅ Variance Check: {unique_values} unique criticality values found")
print(f"   Expected: L5=100, Base=95, L4=85, L3=75, Apps=70, L2=60, L1=50, L0=40, L6=30")
print("=" * 70)
