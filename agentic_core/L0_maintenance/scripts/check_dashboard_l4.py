#!/usr/bin/env python3
"""Quick check of L4 agent count in dashboard"""
from pathlib import Path
import json

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

# Check discovery JSON
data = json.load(open(AGENT_DISCOVERY_JSON))
l4_agents = [a for a in data if a['layer'] == 'L4']
print(f"L4 agents in agent_discovery_full.json: {len(l4_agents)}")

# Check dashboard HTML
html = Path('reports/autonomy_dashboard.html').read_text(encoding='utf-8')
data_start = html.find('const dashboardData = ')
data_end = html.find('];', data_start)
data_str = html[data_start+22:data_end+1]
dashboard_data = json.loads(data_str)

l4_rows = [r for r in dashboard_data if 'L4' in r.get('Territory', '')]
print(f"\nL4 State rows in dashboard HTML: {len(l4_rows)}")
for r in l4_rows:
    print(f"  {r['Territory']}: {r['Total']} agents")

# Check total
total_row = [r for r in dashboard_data if r.get('Territory') == 'TOTAL']
if total_row:
    print(f"\nTotal agents in dashboard: {total_row[0]['Total']}")
