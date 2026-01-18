#!/usr/bin/env python3
"""Direct test of Test 17 logic."""
import json
import re
from pathlib import Path

# Load agents
with open('agent_discovery_full.json', 'r') as f:
    agents = json.load(f)

# Load dashboard data
html_path = Path('agentic_core/L6_observability/dashboards/autonomy_dashboard.html')
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Extract dashboardData
idx = html.find('const dashboardData = [')
end_idx = html.find('];', idx)
json_str = html[idx + len('const dashboardData = '):end_idx + 1]
dashboard_data = json.loads(json_str)

print(f"Loaded {len(dashboard_data)} dashboard rows")
print(f"Loaded {len(agents)} agents from discovery")

# Test 17A: Base Class territories
dashboard_territories = {row['Territory'] for row in dashboard_data if row['Territory'] != 'TOTAL'}
print(f"\nDashboard territories: {len(dashboard_territories)}")

expected_base_classes = [
    "Base/Base Class",
    "L5 Safety/Base Class", 
    "L4 State/Base Class",
    "L3 Orchestration/Base Class",
    "L2 Execution/Base Class",
    "L1 Cognition/Base Class",
    "L0 Maintenance/Base Class",
    "L6_Observability/Base Class"
]

missing = [bc for bc in expected_base_classes if bc not in dashboard_territories]
if missing:
    print(f"Test 17A FAILED: Missing base classes: {missing}")
else:
    print("Test 17A PASSED: All base classes present")

# Test 17B: Agent count
total_dashboard = sum(row.get('Total', 0) for row in dashboard_data if row.get('Territory') != 'TOTAL')
if total_dashboard != len(agents):
    print(f"Test 17B FAILED: Dashboard={total_dashboard}, Discovery={len(agents)}")
else:
    print(f"Test 17B PASSED: {len(agents)} agents")

# Test 17C: Valid data
invalid_rows = []
for row in dashboard_data:
    territory = row.get('Territory', 'UNKNOWN')
    if territory == 'TOTAL':
        continue
    
    total = row.get('Total', 0)
    if total == 0:
        invalid_rows.append(f"{territory}: Total=0")
    
    for field in ['Heal Cap %', 'Test %', 'Observable %', 'Health']:
        val = row.get(field)
        if val is None:
            invalid_rows.append(f"{territory}: {field}=None")
        elif not isinstance(val, (int, float)):
            invalid_rows.append(f"{territory}: {field}={val} (not numeric)")

if invalid_rows:
    print(f"Test 17C FAILED: {len(invalid_rows)} invalid rows")
    for inv in invalid_rows[:10]:
        print(f"  - {inv}")
else:
    print("Test 17C PASSED: All rows valid")
