"""
Verify dashboard data is being refreshed correctly.
Checks timestamp, invocation %, and target values.
"""
import re
import json
from pathlib import Path
from datetime import datetime

dashboard_path = Path("reports/autonomy_dashboard.html")

if not dashboard_path.exists():
    print(f"❌ Dashboard not found: {dashboard_path}")
    exit(1)

html = dashboard_path.read_text(encoding='utf-8')

# Extract timestamp
timestamp_match = re.search(r'Last updated: (.+?)"', html)
if timestamp_match:
    timestamp = timestamp_match.group(1)
    print(f"📅 Dashboard timestamp: {timestamp}")
else:
    print("❌ No timestamp found")

# Extract dashboard data
data_match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
if not data_match:
    print("❌ No dashboardData found")
    exit(1)

rows = json.loads(data_match.group(1))
print(f"📊 Total rows: {len(rows)}")

# Find TOTAL row
total_row = next((r for r in rows if r.get('Territory') == 'TOTAL'), None)
if total_row:
    inv_pct = total_row.get('Invocation %', 'N/A')
    print(f"\n📈 TOTAL Invocation %: {inv_pct}%")
    print(f"   Heal Cap %: {total_row.get('Heal Cap %', 'N/A')}%")
    print(f"   Compliance %: {total_row.get('Compliance %', 'N/A')}%")
else:
    print("❌ No TOTAL row found")

# Check territory rows for targets
non_total = [r for r in rows if r.get('Territory') != 'TOTAL']
print(f"\n🎯 Territory rows: {len(non_total)}")

if non_total:
    # Check L0 Maintenance rows (should have invocation target = 20)
    l0_rows = [r for r in non_total if 'L0 Maintenance' in r.get('Territory', '')]
    if l0_rows:
        print(f"\n🔍 L0 Maintenance territories found: {len(l0_rows)}")
        for row in l0_rows:
            terr = row.get('Territory')
            actual_inv = row.get('Invocation %', 'N/A')
            target_inv = row.get('Target Invocation', 'N/A')
            print(f"   {terr}:")
            print(f"      Actual Invocation: {actual_inv}%")
            print(f"      Target Invocation: {target_inv}")
    
    # Check Infrastructure rows (should have invocation target = 70)
    infra_rows = [r for r in non_total if 'Infrastructure' in r.get('Territory', '') or 'Infrast' in r.get('Territory', '')]
    if infra_rows:
        print(f"\n🔍 Infrastructure territories found: {len(infra_rows)}")
        for row in infra_rows[:3]:  # Show first 3
            terr = row.get('Territory')
            actual_inv = row.get('Invocation %', 'N/A')
            target_inv = row.get('Target Invocation', 'N/A')
            print(f"   {terr}:")
            print(f"      Actual Invocation: {actual_inv}%")
            print(f"      Target Invocation: {target_inv}")
    
    # Check Base Class rows (should have invocation target = N/A)
    base_rows = [r for r in non_total if 'Base Cl' in r.get('Territory', '')]
    if base_rows:
        print(f"\n🔍 Base Class territories found: {len(base_rows)}")
        for row in base_rows:
            terr = row.get('Territory')
            actual_inv = row.get('Invocation %', 'N/A')
            target_inv = row.get('Target Invocation', 'N/A')
            print(f"   {terr}:")
            print(f"      Actual Invocation: {actual_inv}%")
            print(f"      Target Invocation: {target_inv}")

print("\n✅ Dashboard refresh verification complete")
