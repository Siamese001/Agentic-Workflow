from __future__ import annotations
"""
Undo all the incorrect core/ subdirectory moves
"""
import shutil
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.validators.structure_blueprint_2 import (
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

def undo_core_moves() -> Any:
    """Move all files back from */core/ to parent directories"""
    root: Any = Path('.')
    directories: Any = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, 'config', 'observability', 'schemas', SCRIPTS_DIR, 'tools', 'validator', 'prompt_governance']
    moved_count: Any = 0
    for dir_name in directories:
        core_path: Any = root / dir_name / 'core'
        if not core_path.exists():
            continue
        for py_file in core_path.glob('*.py'):
            if py_file.name == '__init__.py':
                continue
            target: Any = core_path.parent / py_file.name
            if target.exists():
                print(f'Skipping {py_file} (target exists)')
                continue
            print(f'Moving {py_file} -> {dir_name}/{py_file.name}')
            shutil.move(str(py_file), str(target))
            moved_count += 1
        try:
            core_path.rmdir()
            print(f'Removed {dir_name}/core/')
        except:
            pass
    print(f'\nTotal files moved back: {moved_count}')
if __name__ == '__main__':
    undo_core_moves()
