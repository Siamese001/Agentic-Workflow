#!/usr/bin/env python3
"""Check actual healing capability in agent_discovery_full.json"""
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

data = json.load(open(AGENT_DISCOVERY_JSON))
print(f"Total agents: {len(data)}")

has_healing = [a for a in data if a.get('has_healing')]
no_healing = [a for a in data if not a.get('has_healing')]

print(f"Has healing: {len(has_healing)}")
print(f"NO healing: {len(no_healing)}")
print(f"Heal Cap %: {len(has_healing)/len(data)*100:.1f}%")

if no_healing:
    print(f"\nAgents WITHOUT healing ({len(no_healing)}):")
    for a in no_healing[:20]:
        print(f"  - {a['class_name']}: {a['path']}")
