import json
import re

# Load discovery
with open('agent_discovery_full.json', 'r') as f:
    agents = json.load(f)

print(f"Discovery file: {len(agents)} agents")

# Load dashboard
with open('agentic_core/L6_observability/dashboards/autonomy_dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
data = json.loads(match.group(1))

total_row = [r for r in data if r['Territory'] == 'TOTAL'][0]
print(f"Dashboard TOTAL row: {total_row['Total']} agents")

territories = [r for r in data if r['Territory'] != 'TOTAL']
territory_sum = sum(r['Total'] for r in territories)
print(f"Sum of all territories: {territory_sum} agents")

# Check which agent is missing
print("\nChecking for discrepancy...")
# Get all agents from realAgentData
agent_data_match = re.search(r'const realAgentData = (\{.*?\});', html, re.DOTALL)
if agent_data_match:
    real_agent_data = json.loads(agent_data_match.group(1))
    dashboard_agents = []
    for territory, data in real_agent_data.items():
        dashboard_agents.extend([a['name'] for a in data.get('agents', [])])
    
    print(f"realAgentData has {len(dashboard_agents)} agents")
    
    discovery_names = {a['class_name'] for a in agents}
    dashboard_names = set(dashboard_agents)
    
    missing_from_dashboard = discovery_names - dashboard_names
    extra_in_dashboard = dashboard_names - discovery_names
    
    if missing_from_dashboard:
        print(f"\nMissing from dashboard ({len(missing_from_dashboard)}):")
        for name in list(missing_from_dashboard)[:5]:
            print(f"  - {name}")
    
    if extra_in_dashboard:
        print(f"\nExtra in dashboard ({len(extra_in_dashboard)}):")
        for name in list(extra_in_dashboard)[:5]:
            print(f"  - {name}")
