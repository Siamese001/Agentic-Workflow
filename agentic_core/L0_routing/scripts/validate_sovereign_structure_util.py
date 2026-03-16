from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "validate_sovereign_structure_util")
emit_determinism_digest("p0", "validate_sovereign_structure_util")

_emit_dispatches_healing_run("p1", "validate_sovereign_structure_util", "L0")
_emit_routes_through("p1", "validate_sovereign_structure_util", "L0")
_emit_escalates_to_human("p1", "validate_sovereign_structure_util", "L0")
_emit_reads_policy_state("p1", "validate_sovereign_structure_util", "L0")

_emit_records_execution_trace("p0", "evidence", "validate_sovereign_structure_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "validate_sovereign_structure_util", "p0_governance")
_emit_snapshots_state("p0", "validate_sovereign_structure_util", "state_snapshot")

"\nSOVEREIGN STRUCTURE VALIDATOR\nEnforces the 3-level depth law for agentic architecture.\n"
import os
import sys
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR
from agentic_core.L0_routing.config.path_constants import (
    APPS_LIC_SUBFOLDER_MAP,
    APPS_RG_SUBFOLDER_MAP,
    APPS_SHARED_SUBFOLDER_MAP,
    CORE_SUBFOLDER_MAP,
    TESTS_DIR,
)

TESTS_L2_SUBFOLDER_MAP = {
    "unit": ["test_agents", "test_utils", "test_core"],
    "integration": ["test_workflows", "test_pipelines"],
}


def check_sovereign_law(root_path: Any) -> Any:
    """Brief description of functionality and purpose."""
    violations: Any = []
    core_path: Any = Path(root_path) / AGENTIC_CORE_DIR
    for l1, l2_list in CORE_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path: Any = Path(core_path) / l1 / l2
            # guardian: allow-path-string
            if not os.path.exists(path):
                violations.append(f"MISSING CORE DEPTH: agentic_core/{l1}/{l2}")
    for l1, l2_list in APPS_RG_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path: Any = Path(root_path) / APPS_RG_DIR / l1 / l2
            # guardian: allow-path-string
            if not os.path.exists(path):
                violations.append(f"MISSING APP DEPTH: apps_rg/{l1}/{l2}")
    for l1, l2_list in APPS_LIC_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path: Any = Path(root_path) / APPS_LIC_DIR / l1 / l2
            # guardian: allow-path-string
            if not os.path.exists(path):
                violations.append(f"MISSING APP DEPTH: apps_lic/{l1}/{l2}")
    for l1, l2_list in APPS_SHARED_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path: Any = Path(root_path) / APPS_SHARED_DIR / l1 / l2
            # guardian: allow-path-string
            if not os.path.exists(path):
                violations.append(f"MISSING APP DEPTH: apps_shared/{l1}/{l2}")
    for l1, l2_list in TESTS_L2_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path: Any = Path(root_path) / TESTS_DIR / l1 / l2
            # guardian: allow-path-string
            if not os.path.exists(path):
                violations.append(f"MISSING TEST DEPTH: tests/{l1}/{l2}")
    if not violations:
        print("\n✅ SOVEREIGN LAW ENFORCED: Your structure is perfect.")
        return 0
    else:
        print(f"\n❌ SOVEREIGN VIOLATIONS FOUND ({len(violations)}):")
        for v in violations:
            print(f"  - {v}")
        return 1


if __name__ == "__main__":
    PROJECT_ROOT: Any = "C:/Git/Agentic-Workflow"
    print(f"--- Auditing Sovereign Structure for {PROJECT_ROOT} ---")
    exit_code: Any = check_sovereign_law(PROJECT_ROOT)
    sys.exit(exit_code)
