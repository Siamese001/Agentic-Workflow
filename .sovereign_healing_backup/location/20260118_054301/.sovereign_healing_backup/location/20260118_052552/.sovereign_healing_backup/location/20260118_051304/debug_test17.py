#!/usr/bin/env python3
"""Debug Test 17 failure."""
import json
import re
from pathlib import Path

# Load agents
with open('agent_discovery_full.json', 'r') as f:
    agents = json.load(f)

# Load dashboard
dashboard_path = Path('agentic_core/L6_observability/dashboards/autonomy_dashboard.html')
with open(dashboard_path, 'r', encoding='utf-8') as f:
    html = f.read()

match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
dashboard_data = json.loads(match.group(1))

# Get expected territories from agent discovery
expected_territories = set()
for agent in agents:
    territory = agent.get('territory', '')
    if territory:
        expected_territories.add(territory)

print(f"Expected territories from discovery: {len(expected_territories)}")
print(f"Sample: {list(expected_territories)[:5]}")

# Get actual territories from dashboard
dashboard_territories = {row['Territory'] for row in dashboard_data if row['Territory'] != 'TOTAL'}
print(f"Dashboard territories: {len(dashboard_territories)}")

# Check base classes
expected_base_classes = [
    'Base/Base Class',
    'L5 Safety/Base Class', 
    'L4 State/Base Class',
    'L3 Orchestration/Base Class',
    'L2 Execution/Base Class',
    'L1 Cognition/Base Class',
    'L6_Observability/Base Class'
]

print("\nBase Class Check:")
for bc in expected_base_classes:
    present = bc in dashboard_territories
    status = "YES" if present else "NO"
    print(f"  {bc}: {status}")

# Check L1 Cognition specifically
print("\nL1 Cognition agents:")
l1_agents = [a for a in agents if 'L1' in a.get('layer', '')]
for a in l1_agents[:3]:
    print(f"  {a['class_name']} - territory: {a.get('territory', 'NONE')}")
