"""Generate simple layer summary table."""
import json
from collections import defaultdict

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
from archives.location_violations.file_utils import safe_read_file, safe_write_file

data = json.load(open(AGENT_DISCOVERY_JSON))

stats = defaultdict(lambda: {'count': 0, 'healing': 0, 'mcp': 0, 'testing': 0, 'tools': 0})

for a in data:
    layer = a.get('layer', 'misc')
    stats[layer]['count'] += 1
    if a.get('has_healing'): stats[layer]['healing'] += 1
    if a.get('mcp_hardened'): stats[layer]['mcp'] += 1
    if a.get('testing') != 'None': stats[layer]['testing'] += 1
    if a.get('has_tools'): stats[layer]['tools'] += 1

print('| Layer | Agents | Healing | MCP Hardened | Testing | Tools |')
print('|-------|--------|---------|--------------|---------|-------|')
for layer in ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, TESTS_DIR, 'misc']:
    s = stats[layer]
    if s['count'] > 0:
        h_pct = 100 * s['healing'] // s['count']
        m_pct = 100 * s['mcp'] // s['count']
        t_pct = 100 * s['testing'] // s['count']
        tl_pct = 100 * s['tools'] // s['count']
        print(f"| {layer} | {s['count']} | {s['healing']} ({h_pct}%) | {s['mcp']} ({m_pct}%) | {s['testing']} ({t_pct}%) | {s['tools']} ({tl_pct}%) |")

total = sum(s['count'] for s in stats.values())
heal = sum(s['healing'] for s in stats.values())
mcp = sum(s['mcp'] for s in stats.values())
test = sum(s['testing'] for s in stats.values())
tools = sum(s['tools'] for s in stats.values())
print(f"| **TOTAL** | **{total}** | **{heal}** ({100*heal//total}%) | **{mcp}** ({100*mcp//total}%) | **{test}** ({100*test//total}%) | **{tools}** ({100*tools//total}%) |")
