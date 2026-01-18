from __future__ import annotations
import ast
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import os
from pathlib import Path
from typing import Any

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
root: Any = Path('C:/Git/Agentic-Workflow')
core: Any = ROOT / AGENTIC_CORE_DIR

def audit_gravity() -> Any:
    """Brief description of functionality and purpose."""
    print('[*] STARTING FINAL GRAVITY AUDIT...')
    leaks: Any = []
    for py_file in CORE.rglob('*.py'):
        if py_file.name == '__init__.py' or 'legacy' in str(py_file):
            continue
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                tree: Any = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if any((x in alias.name for x in [APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR])):
                            leaks.append((py_file.relative_to(ROOT), f'Direct: {alias.name}'))
                elif isinstance(node, ast.ImportFrom):
                    if node.module and any((x in node.module for x in [APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR])):
                        leaks.append((py_file.relative_to(ROOT), f'From: {node.module}'))
        except Exception as e:
            print(f'  [!] Audit Failed for {py_file.name}: {e}')
    if not leaks:
        print('\n[SUCCESS] Gravity is 100% Pure. No downstream leaks detected.')
    else:
        print(f'\n[!] ALERT: Found {len(leaks)} Gravity Violations:')
        for file, reason in leaks:
            print(f'  [X] {file} -> {reason}')
    return leaks
if __name__ == '__main__':
    audit_gravity()
