"""
List agents by layer for batch hardening.

Reads from agent_discovery_full.json - run full_agent_discovery.py first.
"""
import json
import sys

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
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

layer = sys.argv[1] if len(sys.argv) > 1 else APPS_RG_DIR
data = json.load(open(AGENT_DISCOVERY_JSON))
agents = [a for a in data if a.get('layer') == layer]

print(f"{layer} agents ({len(agents)}):")
for a in agents:
    heal = 'H' if a.get('has_healing') else '-'
    mcp = 'M' if a.get('mcp_hardened') else '-'
    test = 'T' if a.get('testing') != 'None' else '-'
    print(f"  [{heal}{mcp}{test}] {a['class_name']} - {a['path']}")
