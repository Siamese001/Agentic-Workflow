#!/usr/bin/env python3
"""Update the dashboard HTML with fresh data from agent_discovery_full.json."""
import json
import re
from pathlib import Path
from collections import defaultdict

# Load agent discovery
with open('C:/Git/Agentic-Workflow/agent_discovery_full.json', 'r', encoding='utf-8') as f:
    agents = json.load(f)

# Group agents by territory (using sub_dir field)
territories = defaultdict(list)
for agent in agents:
    # Use sub_dir for territory grouping, format nicely
    sub_dir = agent.get('sub_dir', 'Unknown')
    # Convert path like "agentic_core/L5_safety" to "L5 Safety"
    if sub_dir and '/' in sub_dir:
        parts = sub_dir.split('/')
        if len(parts) >= 2:
            layer = parts[1].replace('_', ' ').title()
            territory = layer
        else:
            territory = sub_dir
    else:
        territory = sub_dir or 'Unknown'
    territories[territory].append(agent)

# Compute metrics for each territory
dashboard_rows = []
for territory_name, agent_list in sorted(territories.items()):
    total = len(agent_list)
    if total == 0:
        continue
    
    heal_cap = sum(1 for a in agent_list if a.get('has_healing', False))
    heal_inv = sum(1 for a in agent_list if a.get('invocation') == 'Yes')
    has_tests = sum(1 for a in agent_list if a.get('testing') not in ['None', None])
    cc_sum = sum(a.get('cyclomatic_complexity', 1) for a in agent_list)
    typed_sum = sum(a.get('typed_pct', 0) for a in agent_list)
    doc_sum = sum(a.get('documented_pct', 0) for a in agent_list)
    obs_sum = sum(100 if a.get('observability') else 0 for a in agent_list)
    
    avg_cc = round(cc_sum / total, 1)
    heal_cap_pct = round(heal_cap / total * 100, 1)
    heal_inv_pct = round(heal_inv / total * 100, 1)
    test_pct = round(has_tests / total * 100, 1)
    typed_pct = round(typed_sum / total, 1)
    doc_pct = round(doc_sum / total, 1)
    obs_pct = round(obs_sum / total, 1)
    
    health = round((test_pct + heal_inv_pct + obs_pct) / 3, 1)
    risk = "HIGH" if avg_cc > 50 or health < 60 else "MED" if avg_cc > 30 or health < 80 else "LOW"
    
    row = {
        "Territory": territory_name,
        "Total": total,
        "Compliant": heal_cap,
        "Heal Cap %": heal_cap_pct,
        "Heal Invocation %": heal_inv_pct,
        "Invocation %": heal_inv_pct,
        "Test %": test_pct,
        "Observable %": obs_pct,
        "Avg CC": avg_cc,
        "Typed %": typed_pct,
        "Documented %": doc_pct,
        "Health": health,
        "Risk": risk,
    }
    dashboard_rows.append(row)

# Compute TOTAL row
total_agents = sum(r["Total"] for r in dashboard_rows)
def weighted_avg(key): 
    return round(sum(r[key] * r["Total"] for r in dashboard_rows) / total_agents, 1)

total_row = {
    "Territory": "TOTAL",
    "Total": total_agents,
    "Compliant": sum(r["Compliant"] for r in dashboard_rows),
    "Heal Cap %": weighted_avg("Heal Cap %"),
    "Heal Invocation %": weighted_avg("Heal Invocation %"),
    "Invocation %": weighted_avg("Invocation %"),
    "Test %": weighted_avg("Test %"),
    "Observable %": weighted_avg("Observable %"),
    "Avg CC": weighted_avg("Avg CC"),
    "Typed %": weighted_avg("Typed %"),
    "Documented %": weighted_avg("Documented %"),
    "Health": weighted_avg("Health"),
    "Risk": "MED",
}

# Insert TOTAL at beginning
all_rows = [total_row] + dashboard_rows

print(f"=== Dashboard Data Summary ===")
print(f"Total agents: {total_agents}")
print(f"Heal Cap %: {total_row['Heal Cap %']}%")
print(f"Heal Invocation %: {total_row['Heal Invocation %']}%")
print(f"Test %: {total_row['Test %']}%")
print(f"Health: {total_row['Health']}%")

# Now update the dashboard HTML
dashboard_path = Path('C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/autonomy_dashboard.html')
html = dashboard_path.read_text(encoding='utf-8')

# Find and replace the dashboardData JSON
start_marker = 'const dashboardData = ['
end_marker = '];'

start_idx = html.find(start_marker)
end_idx = html.find(end_marker, start_idx) + len(end_marker)

if start_idx == -1 or end_idx == -1:
    print("ERROR: Could not find dashboardData in HTML")
    exit(1)

# Generate new JSON
new_json = json.dumps(all_rows, indent=2)
new_data_block = f'const dashboardData = {new_json};'

# Replace
new_html = html[:start_idx] + new_data_block + html[end_idx:]

# Write back
dashboard_path.write_text(new_html, encoding='utf-8')
print(f"\n✅ Dashboard updated with fresh data!")
print(f"   Path: {dashboard_path}")
