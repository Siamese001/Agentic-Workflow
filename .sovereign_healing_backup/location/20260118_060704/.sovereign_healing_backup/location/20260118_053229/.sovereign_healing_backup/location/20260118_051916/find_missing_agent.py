#!/usr/bin/env python3
"""Find which agent is missing from dashboard."""
import json
import re
from pathlib import Path

# Load agents
with open('agent_discovery_full.json', 'r') as f:
    agents = json.load(f)

# Load dashboard
with open('agentic_core/L6_observability/dashboards/autonomy_dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Get realAgentData
match = re.search(r'const realAgentData = (\{.*?\});', html, re.DOTALL)
real_agent_data = json.loads(match.group(1))

# Count agents in dashboard
dashboard_agent_names = set()
for territory, data in real_agent_data.items():
    for agent in data.get('agents', []):
        dashboard_agent_names.add(agent['name'])

# Find missing
discovery_names = {a['class_name'] for a in agents}
missing = discovery_names - dashboard_agent_names
print(f"Discovery: {len(discovery_names)} agents")
print(f"Dashboard: {len(dashboard_agent_names)} agents")
print(f"Missing: {len(missing)}")
for m in missing:
    agent = next(a for a in agents if a['class_name'] == m)
    print(f"  {m}")
    print(f"    layer: {agent.get('layer')}")
    print(f"    path: {agent.get('path')}")
    print(f"    territory: {agent.get('territory')}")
