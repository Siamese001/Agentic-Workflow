import json
from pathlib import Path

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

agents = json.loads(Path(AGENT_DISCOVERY_JSON).read_text())
l6_agents = [a for a in agents if 'L6' in a.get('path', '')]

print(f'Found {len(l6_agents)} L6 agents:')
for a in l6_agents:
    print(f"  {a['class_name']}: layer={a.get('layer')}, path={a['path']}")
