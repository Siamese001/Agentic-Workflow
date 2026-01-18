"""Check which BaseAgent classes are now discovered."""
import json

from agentic_core.L5_safety.validators.structure_blueprint_1 import (
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

with open(AGENT_DISCOVERY_JSON, 'r') as f:
    agents = json.load(f)

base_agents = [a for a in agents if 'BaseAgent' in a.get('class_name', '')]
print(f"Found {len(base_agents)} BaseAgent classes:")
for a in base_agents:
    path = a.get('relative_path') or a.get('path') or a.get('file_path', 'unknown')
    print(f"  {a['class_name']}: {path}")
