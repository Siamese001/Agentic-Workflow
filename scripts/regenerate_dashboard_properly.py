#!/usr/bin/env python3
"""Properly regenerate dashboard from agent_discovery_full.json with correct territory structure."""
import json
from pathlib import Path
from collections import defaultdict

# Load agent discovery
with open('C:/Git/Agentic-Workflow/agent_discovery_full.json', 'r', encoding='utf-8') as f:
    agents = json.load(f)

print(f"Total agents: {len(agents)}")

# Group agents by detailed territory (layer + sub_dir)
territories = defaultdict(list)
for agent in agents:
    layer = agent.get('layer', 'Unknown')
    sub_dir = agent.get('sub_dir', '')
    
    # Create detailed territory name based on path structure
    if layer.startswith('L'):
        # Core layers: extract sub-category from sub_dir
        parts = sub_dir.split('/')
        if len(parts) >= 2:
            # e.g., "agentic_core/L5_safety" -> look at next level
            if 'base_agents' in sub_dir:
                territory = f"{layer}/Base Class"
            elif 'validators' in sub_dir:
                territory = f"{layer}/Validators"
            elif 'guardrails' in sub_dir:
                territory = f"{layer}/Guardrails"
            elif 'gravity' in sub_dir.lower():
                territory = f"{layer}/Gravity"
            elif 'red_team' in sub_dir or 'red-team' in sub_dir:
                territory = f"{layer}/Red Teaming"
            elif 'workflow_engines' in sub_dir or 'orchestration' in sub_dir:
                if 'base' in agent.get('path', '').lower():
                    territory = f"{layer}/Base Class"
                elif any(x in agent.get('path', '').lower() for x in ['infrastructure', 'mcp', 'connection']):
                    territory = f"{layer}/Infrastructure"
                elif any(x in agent.get('path', '').lower() for x in ['specialized', 'coverage', 'meta']):
                    territory = f"{layer}/Specialized"
                else:
                    territory = f"{layer}/Core"
            elif 'state' in sub_dir.lower():
                if 'base' in agent.get('path', '').lower():
                    territory = f"{layer}/Base Class"
                elif any(x in agent.get('path', '').lower() for x in ['infrastructure', 'filesystem']):
                    territory = f"{layer}/Infrastructure"
                elif any(x in agent.get('path', '').lower() for x in ['specialized', 'validation']):
                    territory = f"{layer}/Specialized"
                else:
                    territory = f"{layer}/Core"
            elif 'execution' in sub_dir.lower() or 'tool' in sub_dir.lower():
                if 'base' in agent.get('path', '').lower():
                    territory = f"{layer}/Base Class"
                elif any(x in agent.get('path', '').lower() for x in ['specialized', 'dynamic', 'interface']):
                    territory = f"{layer}/Specialized"
                else:
                    territory = f"{layer}/Core"
            elif 'cognition' in sub_dir.lower():
                if 'base' in agent.get('path', '').lower():
                    territory = f"{layer}/Base Class"
                elif any(x in agent.get('path', '').lower() for x in ['specialized', 'contract', 'exerciser']):
                    territory = f"{layer}/Specialized"
                else:
                    territory = f"{layer}/Core"
            elif 'maintenance' in sub_dir.lower():
                if any(x in agent.get('path', '').lower() for x in ['infrastructure', 'scripts']):
                    territory = f"{layer}/Infrastructure"
                else:
                    territory = f"{layer}/Core"
            elif 'observability' in sub_dir.lower():
                if 'metrics' in agent.get('path', '').lower():
                    territory = "L6_Observability/Metrics"
                elif 'telemetry' in agent.get('path', '').lower():
                    territory = "L6_Observability/Telemetry"
                elif 'tracing' in agent.get('path', '').lower():
                    territory = "L6_Observability/Tracing"
                elif 'compliance' in agent.get('path', '').lower():
                    territory = "L6_Observability/Compliance"
                else:
                    territory = f"{layer}/Metrics"
            else:
                territory = layer
        else:
            territory = layer
    elif 'apps_lic' in sub_dir:
        territory = "Apps Lic"
    elif 'apps_rg' in sub_dir:
        territory = "Apps Rg"
    elif 'apps_shared' in sub_dir:
        territory = "Apps Shared"
    else:
        territory = layer
    
    territories[territory].append(agent)

print(f"\nTerritories found: {len(territories)}")
for t, agents_list in sorted(territories.items()):
    heal_count = sum(1 for a in agents_list if a.get('has_healing'))
    print(f"  {t}: {len(agents_list)} agents ({heal_count} healed = {heal_count/len(agents_list)*100:.1f}%)")

# Build dashboard rows
rows = []
for territory_name in sorted(territories.keys()):
    agents_list = territories[territory_name]
    total = len(agents_list)
    
    heal_cap = sum(1 for a in agents_list if a.get('has_healing'))
    heal_inv = sum(1 for a in agents_list if a.get('invocation') == 'Yes')
    test = sum(1 for a in agents_list if a.get('has_tests'))
    obs = sum(1 for a in agents_list if a.get('observability'))
    cc_sum = sum(a.get('cyclomatic_complexity', 1) for a in agents_list)
    typed_sum = sum(a.get('typed_pct', 0) for a in agents_list)
    doc_sum = sum(a.get('documented_pct', 0) for a in agents_list)
    
    avg_cc = round(cc_sum / total, 1)
    heal_cap_pct = round(heal_cap / total * 100, 1)
    heal_inv_pct = round(heal_inv / total * 100, 1)
    test_pct = round(test / total * 100, 1)
    obs_pct = round(obs / total * 100, 1)
    typed_pct = round(typed_sum / total, 1)
    doc_pct = round(doc_sum / total, 1)
    
    health = round((test_pct + heal_inv_pct + obs_pct) / 3, 1)
    risk = "HIGH" if avg_cc > 12 or health < 60 else "MED" if avg_cc > 8 or health < 80 else "LOW"
    
    row = {
        "Territory": territory_name,
        "Total": total,
        "Compliant": heal_cap,
        "Heal Cap %": heal_cap_pct,
        "Heal Invocation %": heal_inv_pct,
        "Test %": test_pct,
        "Observable %": obs_pct,
        "Avg CC": avg_cc,
        "Typed %": typed_pct,
        "Documented %": doc_pct,
        "Health": health,
        "Risk": risk
    }
    rows.append(row)

# Build TOTAL row
total_agents = sum(r["Total"] for r in rows)
def weighted_avg(key):
    return round(sum(r[key] * r["Total"] for r in rows) / total_agents, 1)

total_row = {
    "Territory": "TOTAL",
    "Total": total_agents,
    "Compliant": sum(r["Compliant"] for r in rows),
    "Heal Cap %": weighted_avg("Heal Cap %"),
    "Heal Invocation %": weighted_avg("Heal Invocation %"),
    "Test %": weighted_avg("Test %"),
    "Observable %": weighted_avg("Observable %"),
    "Avg CC": weighted_avg("Avg CC"),
    "Typed %": weighted_avg("Typed %"),
    "Documented %": weighted_avg("Documented %"),
    "Health": weighted_avg("Health"),
    "Risk": "HIGH" if weighted_avg("Health") < 70 else "MED" if weighted_avg("Health") < 85 else "LOW"
}

# Insert TOTAL at the beginning
all_rows = [total_row] + rows

print(f"\n=== TOTAL ROW ===")
print(f"  Total: {total_row['Total']}")
print(f"  Heal Cap %: {total_row['Heal Cap %']}%")
print(f"  Health: {total_row['Health']}%")

# Update dashboard HTML
dashboard_path = Path('C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/autonomy_dashboard.html')
html = dashboard_path.read_text(encoding='utf-8')

# Replace dashboardData
start_marker = 'const dashboardData = ['
end_marker = '];'
start_idx = html.find(start_marker)
end_idx = html.find(end_marker, start_idx) + len(end_marker)

new_json = json.dumps(all_rows, indent=2)
new_data_block = f'const dashboardData = {new_json};'
new_html = html[:start_idx] + new_data_block + html[end_idx:]

dashboard_path.write_text(new_html, encoding='utf-8')

print(f"\n✅ Dashboard regenerated with {len(all_rows)} rows (including TOTAL)")
print(f"   Path: {dashboard_path}")
