"""Verify registry integrity matches sovereign state."""
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

# Load both files
with open(AGENT_DISCOVERY_JSON) as f:
    registry = json.load(f)

with open('sovereign_state_final.json') as f:
    state = json.load(f)

# Compare counts
reg_count = len(registry)
state_count = state['baseline_metadata']['agent_count']

print(f"Registry agents: {reg_count}")
print(f"State agents: {state_count}")
print(f"Match: {reg_count == state_count}")

if reg_count == state_count:
    print("\n✅ INTEGRITY VERIFIED - Registry matches sovereign state")
else:
    print(f"\n❌ MISMATCH - Registry has {reg_count}, state expects {state_count}")
