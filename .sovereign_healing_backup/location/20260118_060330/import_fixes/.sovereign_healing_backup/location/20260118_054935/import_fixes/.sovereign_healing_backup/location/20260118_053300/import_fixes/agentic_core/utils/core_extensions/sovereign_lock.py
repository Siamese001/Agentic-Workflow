from __future__ import annotations
import os
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import re
import sys
from pathlib import Path
from typing import Any

from agentic_core.config.blueprint_sovereign.structure_blueprint_1 import (
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
root: Any = Path.cwd()
core: Any = ROOT / AGENTIC_CORE_DIR

def enforce_gravity() -> Any:
    """Ensures no file in agentic_core reaches 'down' into apps."""
    print('[*] ENFORCING GRAVITY...')
    violations: Any = 0
    forbidden: Any = [APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR]
    for py_file in CORE.rglob('*.py'):
        if py_file.name == '__init__.py':
            continue
        content: Any = py_file.read_text(encoding='utf-8')
        for f in forbidden:
            if f in content:
                if re.search(f'^(import\\s+{f}|from\\s+{f})', content, re.M):
                    print(f'  [X] GRAVITY BREACH: {py_file.relative_to(ROOT)} imports {f}!')
                    violations += 1
    return violations

def enforce_depth() -> Any:
    """Ensures every file is EXACTLY at Depth 4. No shallower, no deeper."""
    print('[*] ENFORCING ABSOLUTE DEPTH-4 MANDATE...')
    violations: Any = 0
    for py_file in CORE.rglob('*.py'):
        if py_file.name == '__init__.py':
            continue
        parts: Any = py_file.relative_to(CORE).parts
        if len(parts) != 3:
            depth_status: Any = 'SHALLOW' if len(parts) < 3 else 'TUNNEL'
            print(f'  [X] {depth_status} VIOLATION: {py_file.relative_to(ROOT)}')
            print(f'      Actual: {len(parts) + 1} | Required: 4')
            violations += 1
    return violations

def check_airlocks() -> Any:
    """Ensures __init__.py files are minimal (under 50 lines)."""
    print('[*] CHECKING AIRLOCK HYGIENE...')
    violations: Any = 0
    for init_file in CORE.rglob('__init__.py'):
        lines: Any = init_file.read_text(encoding='utf-8').splitlines()
        if len(lines) > 50:
            print(f'  [X] HEAVY AIRLOCK: {init_file.relative_to(ROOT)} has {len(lines)} lines. Keep it lean!')
            violations += 1
    return violations
if __name__ == '__main__':
    v1: Any = enforce_gravity()
    v2: Any = enforce_depth()
    v3: Any = check_airlocks()
    total: Any = v1 + v2 + v3
    if total > 0:
        print(f'\n[BLOCK] {total} Sovereignty Violations detected. Fix these before committing.')
        sys.exit(1)
    else:
        print('\n[SUCCESS] Sovereign Core is locked and compliant. Move forward.')
        sys.exit(0)
