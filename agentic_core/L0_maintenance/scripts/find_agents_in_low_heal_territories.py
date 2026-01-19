#!/usr/bin/env python3
"""Find actual agent files that belong to low heal capability territories."""
import json
from pathlib import Path
from archives.location_violations.sovereign_index import SovereignIndex
from archives.location_violations.file_utils import safe_read_file, safe_write_file

# Read the dashboard file
with open('C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/autonomy_dashboard.html', 'r', encoding='utf-8') as f:
    data = f.read()

# Extract JSON data
start = data.find('const dashboardData = [')
end = data.find('];', start) + 1
json_str = data[start+21:end]

# Parse JSON
territories = json.loads(json_str)

# Find all territories and their heal cap
print("=== All Territories with Heal Cap % ===")
for t in sorted(territories, key=lambda x: x.get('Heal Cap %', 100)):
    if t['Territory'] == 'TOTAL':
        continue
    heal_cap = t.get('Heal Cap %', 100)
    total = t.get('Total', 0)
    if heal_cap < 100:
        print(f"  {t['Territory']}: {heal_cap}% ({total} agents)")

# Now let's find agents in the repository that might match these territories
# Phase 4.1: Use ssot_discovery instead of rglob
from agentic_core.utils.ssot_discovery import get_agent_files
print("\n=== Searching for agents in L1 Cognition ===")
l1_agents = [f for f in get_agent_files(Path('C:/Git/Agentic-Workflow/agentic_core/L1_cognition'))]
for agent in l1_agents:
    content = agent.read_text(encoding='utf-8', errors='ignore')
    has_heal = 'def heal_repository' in content
    print(f"  {'✅' if has_heal else '❌'} {agent.name}")

print("\n=== Searching for agents in L3 Orchestration ===")
l3_agents = [f for f in get_agent_files(Path('C:/Git/Agentic-Workflow/agentic_core/L3_orchestration'))]
for agent in l3_agents:
    content = agent.read_text(encoding='utf-8', errors='ignore')
    has_heal = 'def heal_repository' in content
    print(f"  {'✅' if has_heal else '❌'} {agent.name}")

print("\n=== Agents MISSING heal_repository (need to fix) ===")
all_agents = get_agent_files(Path('C:/Git/Agentic-Workflow/agentic_core'))
missing = []
for agent in all_agents:
    content = agent.read_text(encoding='utf-8', errors='ignore')
    if 'def heal_repository' not in content:
        missing.append(agent)
        print(f"  ❌ {agent.relative_to(Path('C:/Git/Agentic-Workflow'))}")

print(f"\nTotal agents missing heal_repository: {len(missing)}")
