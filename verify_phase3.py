#!/usr/bin/env python3
"""Verify Phase 3 metadata and usage metrics"""
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
print("PHASE 3 METADATA & USAGE VERIFICATION")
print("=" * 70)
print(f"\nTOTAL Row:")
print(f"  Metadata %: {data[0]['Metadata %']}")
print(f"  Used %: {data[0]['Used %']}")

print(f"\nSample Territory Values:")
print("-" * 70)
for row in data[1:8]:
    territory = row['Territory'][:40]
    metadata = row['Metadata %']
    used = row['Used %']
    print(f"  {territory:40s} Metadata={metadata:5.1f}% Used={used:5.1f}%")

# Check for variance
metadata_values = [r['Metadata %'] for r in data[1:]]
used_values = [r['Used %'] for r in data[1:]]

print(f"\n✅ Metadata % variance: {len(set(metadata_values))} unique values")
print(f"   Range: {min(metadata_values):.1f}% - {max(metadata_values):.1f}%")
print(f"✅ Used % variance: {len(set(used_values))} unique values")
print(f"   Range: {min(used_values):.1f}% - {max(used_values):.1f}%")
print("=" * 70)
