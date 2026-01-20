from __future__ import annotations
import shutil
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from pathlib import Path
from typing import Any

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
from agentic_core.utils.sovereign_index import SovereignIndex
root: Any = Path('C:/Git/Agentic-Workflow')
core: Any = ROOT / AGENTIC_CORE_DIR
obs_runtime: Any = CORE / 'observability/P1_core/runtime'
obs_p1: Any = CORE / 'observability/P1_core'

def move_runtime_files_up() -> Any:
    """Brief description of functionality and purpose."""
    print('[*] MOVING runtime files up to observability/P1_core...')
    moved: Any = 0
    if not OBS_RUNTIME.exists():
        print('[!] Runtime directory not found')
        return
    # Phase 6.8: Use ssot_discovery instead of glob
    from agentic_core.utils.ssot_discovery import get_python_files
    for py_file in get_python_files(OBS_RUNTIME):
        if py_file.name == '__init__.py':
            continue
        target: Any = OBS_P1 / f'runtime_{py_file.name}'
        counter: Any = 1
        while target.exists():
            target: Any = OBS_P1 / f'runtime_{counter}_{py_file.name}'
            counter += 1
        try:
            shutil.move(str(py_file), str(target))
            print(f'  [✓] {py_file.name} -> {target.name}')
            moved += 1
        except Exception as e:
            print(f'  [X] Failed: {py_file.name} - {e}')
    try:
        if OBS_RUNTIME.exists() and (not any(OBS_RUNTIME.iterdir())):
            OBS_RUNTIME.rmdir()
            print(f'\n[✓] Removed empty directory: runtime/')
    except:
        pass
    print(f'\n[OK] MOVE COMPLETE. {moved} files moved to depth-4.')
if __name__ == '__main__':
    move_runtime_files_up()
