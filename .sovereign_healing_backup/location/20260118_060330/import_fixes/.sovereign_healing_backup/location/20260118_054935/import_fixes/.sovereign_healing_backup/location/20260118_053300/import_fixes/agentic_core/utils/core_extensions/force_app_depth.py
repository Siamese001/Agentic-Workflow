from __future__ import annotations
import os
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import shutil
from pathlib import Path

# [SSOT IMPORT] Structure blueprint is the single source of truth
from typing import Any
from agentic_core.config.blueprint_sovereign.structure_blueprint_1 import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
    get_validated_project_root,
    safe_path_join,
)

# FILESYSTEM COMPLIANCE: Use safe_path_join for all file operations
PROJECT_ROOT = get_validated_project_root()
CORE = safe_path_join(PROJECT_ROOT, 'agentic_core')
APPS = [
    safe_path_join(PROJECT_ROOT, 'apps_lic'),
    safe_path_join(PROJECT_ROOT, 'apps_rg')
]

def force_app_depth() -> Any:
    """Brief description of functionality and purpose."""
    print('[*] FORCING DEPTH-4 ON TERRITORIES...')
    for app_path in APPS:
        if not app_path.exists():
            continue
        print(f'\n[HARDENING] {app_path.name}...')
        for engine_folder in app_path.glob('*_engine'):
            dest: Any = CORE / 'L2_execution' / 'P3_engines' / engine_folder.name
            dest.mkdir(parents=True, exist_ok=True)
            for item in engine_folder.iterdir():
                if item.is_dir() and item.name.startswith('__'):
                    continue
                shutil.move(str(item), str(dest / item.name))
            try:
                shutil.rmtree(str(engine_folder))
            except:
                pass
            print(f'  [✓] ENGINE EXTRICATED: {engine_folder.name} -> Core/L2_execution/P3_engines')
        for layer_folder in app_path.glob('L*'):
            if not layer_folder.is_dir():
                continue
            layer_map: Any = {'L0': 'L1_cognition', 'L1': 'L1_cognition', 'L2': 'L2_execution', 'L3': 'L3_orchestration'}
            target_layer: Any = layer_map.get(layer_folder.name, layer_folder.name)
            dest: Any = CORE / target_layer / 'P1_core'
            dest.mkdir(parents=True, exist_ok=True)
            for item in layer_folder.iterdir():
                if item.is_dir() and item.name.startswith('__'):
                    continue
                shutil.move(str(item), str(dest / item.name))
            try:
                shutil.rmtree(str(layer_folder))
            except:
                pass
            print(f'  [✓] LAYER ANNEXED: {layer_folder.name} -> Core/{target_layer}/P1_core')
        app_p1: Any = app_path / 'P1_core'
        app_p1.mkdir(parents=True, exist_ok=True)
        if not (app_p1 / '__init__.py').exists():
            (app_p1 / '__init__.py').write_text('"""App Core Implementation"""\n')
        for py_file in app_path.glob('*.py'):
            if py_file.name == '__init__.py':
                continue
            if 'sovereign_lock' in py_file.name:
                continue
            shutil.move(str(py_file), str(app_p1 / py_file.name))
            print(f'  [!] DEPTH CORRECTION: {py_file.name} -> {app_path.name}/P1_core')
if __name__ == '__main__':
    force_app_depth()
