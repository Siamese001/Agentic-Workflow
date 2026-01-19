#!/usr/bin/env python3
"""Debug Test 17 failure - v2."""
import json
import re
from pathlib import Path

# Load agents
with open('agent_discovery_full.json', 'r') as f:
    agents = json.load(f)

# Load dashboard
with open('agentic_core/L6_observability/dashboards/autonomy_dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Try both regex patterns
match1 = re.search(r'const dashboardData = (\[[\s\S]*?\]);', html)
dashboard_data = None
if not match1:
    # Find where dashboardData starts
    idx = html.find('const dashboardData = [')
    if idx != -1:
        # Find the closing ];
        end_idx = html.find('];', idx)
        if end_idx != -1:
            json_str = html[idx + len('const dashboardData = '):end_idx + 1]
            dashboard_data = json.loads(json_str)
            print(f"Loaded {len(dashboard_data)} rows via manual parsing")
    else:
        print("Could not find dashboardData")
        exit(1)
else:
    dashboard_data = json.loads(match1.group(1))
    print(f"Loaded {len(dashboard_data)} rows via regex")

# Get expected territories from agent discovery
expected_territories = set()
for agent in agents:
    territory = agent.get('territory', '')
    if territory:
        expected_territories.add(territory)

print(f"\nExpected territories from discovery: {len(expected_territories)}")

# Get actual territories from dashboard
dashboard_territories = {row['Territory'] for row in dashboard_data if row['Territory'] != 'TOTAL'}
print(f"Dashboard territories: {len(dashboard_territories)}")

# Check for any territories in discovery but missing from dashboard
missing_territories = []
for territory in expected_territories:
    if territory not in dashboard_territories:
        agent_count = len([a for a in agents if a.get('territory') == territory])
        if agent_count > 0:
            missing_territories.append((territory, agent_count))

if missing_territories:
    print(f"\nMissing territories from dashboard:")
    for t, count in missing_territories:
        print(f"  {t} ({count} agents)")
else:
    print("\nNo missing territories!")

# Check expected base classes
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

print(f"\nBase Class Check ({len(expected_base_classes)} expected):")
for bc in expected_base_classes:
    in_dashboard = bc in dashboard_territories
    status = "YES" if in_dashboard else "NO"
    print(f"  {bc}: {status}")
