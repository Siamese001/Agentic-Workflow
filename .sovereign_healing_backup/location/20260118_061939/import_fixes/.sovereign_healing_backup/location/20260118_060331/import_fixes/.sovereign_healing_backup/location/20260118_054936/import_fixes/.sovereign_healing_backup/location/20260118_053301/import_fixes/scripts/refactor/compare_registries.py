"""Compare backup and current agent registries."""
import json
from pathlib import Path

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

backup_path = Path('.refactor_backups/agent_discovery_full.json.bak')
current_path = Path(AGENT_DISCOVERY_JSON)

if backup_path.exists():
    with open(backup_path) as f:
        old = json.load(f)
else:
    print("No backup registry found")
    exit(1)

with open(current_path) as f:
    new = json.load(f)

old_names = {a['class_name'] for a in old}
new_names = {a['class_name'] for a in new}

missing = old_names - new_names
gained = new_names - old_names

print(f"Backup registry: {len(old)} agents")
print(f"Current registry: {len(new)} agents")
print(f"Delta: {len(new) - len(old)}")
print()

if missing:
    print(f"Missing from current ({len(missing)}):")
    for name in sorted(missing):
        # Find where it was
        for agent in old:
            if agent['class_name'] == name:
                print(f"  - {name} (was in {agent['path']})")
                break
else:
    print("No agents missing from current registry")

if gained:
    print()
    print(f"Gained in current ({len(gained)}):")
    for name in sorted(gained):
        for agent in new:
            if agent['class_name'] == name:
                print(f"  + {name} (now in {agent['path']})")
                break
