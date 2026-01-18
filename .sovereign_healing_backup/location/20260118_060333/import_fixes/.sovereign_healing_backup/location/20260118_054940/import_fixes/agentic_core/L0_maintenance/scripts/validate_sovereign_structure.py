from __future__ import annotations
"""
SOVEREIGN STRUCTURE VALIDATOR
Enforces the 3-level depth law for agentic architecture.
"""
import os
import sys
from agentic_core.L5_safety.validators.structure_blueprint_1 import APPS_LIC_SUBFOLDER_MAP, APPS_RG_SUBFOLDER_MAP, APPS_SHARED_SUBFOLDER_MAP, CORE_SUBFOLDER_MAP, TESTS_L2_SUBFOLDER_MAP
from typing import Any

def check_sovereign_law(root_path: Any) -> Any:
    """Brief description of functionality and purpose."""
    violations: Any = []
    core_path: Any = os.path.join(root_path, 'agentic_core')
    for l1, l2_list in CORE_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path: Any = os.path.join(core_path, l1, l2)
            if not os.path.exists(path):
                violations.append(f'MISSING CORE DEPTH: agentic_core/{l1}/{l2}')
    for l1, l2_list in APPS_RG_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path: Any = os.path.join(root_path, 'apps_rg', l1, l2)
            if not os.path.exists(path):
                violations.append(f'MISSING APP DEPTH: apps_rg/{l1}/{l2}')
    for l1, l2_list in APPS_LIC_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path: Any = os.path.join(root_path, 'apps_lic', l1, l2)
            if not os.path.exists(path):
                violations.append(f'MISSING APP DEPTH: apps_lic/{l1}/{l2}')
    for l1, l2_list in APPS_SHARED_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path: Any = os.path.join(root_path, 'apps_shared', l1, l2)
            if not os.path.exists(path):
                violations.append(f'MISSING APP DEPTH: apps_shared/{l1}/{l2}')
    for l1, l2_list in TESTS_L2_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path: Any = os.path.join(root_path, 'tests', l1, l2)
            if not os.path.exists(path):
                violations.append(f'MISSING TEST DEPTH: tests/{l1}/{l2}')
    if not violations:
        print('\n✅ SOVEREIGN LAW ENFORCED: Your structure is perfect.')
        return 0
    else:
        print(f'\n❌ SOVEREIGN VIOLATIONS FOUND ({len(violations)}):')
        for v in violations:
            print(f'  - {v}')
        return 1
if __name__ == '__main__':
    PROJECT_ROOT: Any = 'C:/Git/Agentic-Workflow'
    print(f'--- Auditing Sovereign Structure for {PROJECT_ROOT} ---')
    exit_code: Any = check_sovereign_law(PROJECT_ROOT)
    sys.exit(exit_code)
