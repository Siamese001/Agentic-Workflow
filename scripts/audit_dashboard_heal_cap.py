#!/usr/bin/env python3
"""Audit dashboard heal capability percentages and compare with actual agent data."""
import json
import re
from pathlib import Path
from collections import defaultdict

# Load dashboard HTML
dashboard_path = Path('C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/autonomy_dashboard.html')
html = dashboard_path.read_text(encoding='utf-8')

# Extract dashboardData JSON
start_marker = 'const dashboardData = ['
end_marker = '];'
start_idx = html.find(start_marker)
end_idx = html.find(end_marker, start_idx) + len(end_marker)
json_str = html[start_idx+len(start_marker)-1:end_idx-1]
territories = json.loads(json_str)

print("=== DASHBOARD HEAL CAPABILITY AUDIT ===\n")

# Find territories with <50% heal capability
low_heal = []
for t in territories:
    heal_cap = t.get('Heal Cap %', 0)
    if t['Territory'] != 'TOTAL' and heal_cap < 50:
        low_heal.append({
            'territory': t['Territory'],
            'heal_cap': heal_cap,
            'total': t['Total'],
            'compliant': t['Compliant']
        })

if low_heal:
    print(f"❌ Found {len(low_heal)} territories with <50% Heal Cap %:\n")
    for item in low_heal:
        print(f"  - {item['territory']}: {item['heal_cap']}% ({item['compliant']}/{item['total']} agents)")
else:
    print("✅ No territories with <50% Heal Cap %")

# Check TOTAL row
total_row = next((t for t in territories if t['Territory'] == 'TOTAL'), None)
if total_row:
    print(f"\n=== TOTAL ROW ===")
    print(f"  Heal Cap %: {total_row['Heal Cap %']}%")
    print(f"  Total agents: {total_row['Total']}")
    print(f"  Compliant: {total_row['Compliant']}")

# Load actual agent discovery data
discovery_path = Path('C:/Git/Agentic-Workflow/agent_discovery_full.json')
if discovery_path.exists():
    with open(discovery_path, 'r', encoding='utf-8') as f:
        agents = json.load(f)
    
    print(f"\n=== ACTUAL AGENT DATA ===")
    print(f"  Total agents: {len(agents)}")
    print(f"  Agents with healing: {sum(1 for a in agents if a.get('has_healing'))}")
    print(f"  Actual Heal Cap %: {sum(1 for a in agents if a.get('has_healing')) / len(agents) * 100:.1f}%")
    
    # Check discrepancy
    dashboard_total = total_row['Total']
    actual_total = len(agents)
    if dashboard_total != actual_total:
        print(f"\n⚠️  DISCREPANCY: Dashboard shows {dashboard_total} agents but discovery has {actual_total} agents")
        print(f"   Difference: {actual_total - dashboard_total} agents")

print("\n=== ALL TERRITORIES ===")
for t in territories:
    if t['Territory'] != 'TOTAL':
        heal_cap = t.get('Heal Cap %', 0)
        marker = "❌" if heal_cap < 50 else "⚠️" if heal_cap < 100 else "✅"
        print(f"{marker} {t['Territory']}: {heal_cap}% ({t['Compliant']}/{t['Total']})")
