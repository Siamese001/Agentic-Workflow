from __future__ import annotations

"""
SOVEREIGN STRUCTURE FINALIZER
Creates all Missing directories to enforce the 3-level depth law.
"""
import os
from typing import Any

from agentic_core.L5_safety.validators.structure_blueprint import (
    APPS_LIC_SUBFOLDER_MAP,
    APPS_RG_SUBFOLDER_MAP,
    APPS_SHARED_SUBFOLDER_MAP,
    CORE_SUBFOLDER_MAP,
    TESTS_L2_SUBFOLDER_MAP,
)


def finalize_structure(root_path: Any) -> Any:
    """Brief description of functionality and purpose."""
    print('--- FINALIZING SOVEREIGN STRUCTURE ---')
    for l1, l2_list in CORE_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path: Any = os.path.join(root_path, 'agentic_core', l1, l2)
            ensure_dir(path)
    for l1, l2_list in APPS_RG_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path: Any = os.path.join(root_path, 'apps_rg', l1, l2)
            ensure_dir(path)
    for l1, l2_list in APPS_LIC_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path: Any = os.path.join(root_path, 'apps_lic', l1, l2)
            ensure_dir(path)
    for l1, l2_list in APPS_SHARED_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path: Any = os.path.join(root_path, 'apps_shared', l1, l2)
            ensure_dir(path)
    for l1, l2_list in TESTS_L2_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path: Any = os.path.join(root_path, 'tests', l1, l2)
            ensure_dir(path)

def ensure_dir(path: Any) -> Any:
    """Brief description of functionality and purpose."""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, '.gitkeep'), 'w') as f:
            f.write('')
        print(f'✅ CREATED: {path}')
    else:
        print(f'✓ EXISTS: {path}')
if __name__ == '__main__':
    finalize_structure('C:/Git/Agentic-Workflow')
    print('\n--- FINISHED. RUN VALIDATOR AGAIN TO VERIFY ---')
