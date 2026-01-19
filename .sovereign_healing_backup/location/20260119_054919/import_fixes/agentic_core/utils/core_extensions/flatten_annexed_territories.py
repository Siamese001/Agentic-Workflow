from __future__ import annotations
"""
Flatten annexed territories to SSOT-compliant depth.
[SSOT] All depth requirements derived from SOVEREIGN_REGISTRY in structure_blueprint.py
"""
import os
import shutil
from pathlib import Path
from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_REGISTRY
from typing import Any
from agentic_core.utils.sovereign_index import SovereignIndex
root: Any = Path('C:/Git/Agentic-Workflow')
core: Any = ROOT / 'agentic_core'
required_depth: Any = SOVEREIGN_REGISTRY['agentic_core']['depth']
annexed_layers: Any = ['config', 'observability', 'prompt_governance', 'schemas']

def flatten_annexed() -> Any:
    """Brief description of functionality and purpose."""
    print(f'[*] FLATTENING ANNEXED TERRITORIES TO DEPTH-{REQUIRED_DEPTH}...')
    moved: Any = 0
    for layer in ANNEXED_LAYERS:
        layer_path: Any = CORE / layer
        if not layer_path.exists():
            continue
        print(f'\n[*] Processing layer: {layer}')
        for stage_dir in layer_path.iterdir():
            if not stage_dir.is_dir() or stage_dir.name == '__pycache__':
                continue
            for subdir in stage_dir.rglob('*'):
                if subdir.is_file() and subdir.suffix == '.py':
                    rel_path: Any = subdir.relative_to(CORE)
                    parts: Any = rel_path.parts
                    if len(parts) > REQUIRED_DEPTH - 1:
                        target: Any = CORE / parts[0] / parts[1] / subdir.name
                        if target.exists():
                            target: Any = CORE / parts[0] / parts[1] / f'{parts[2]}_{subdir.name}'
                        try:
                            shutil.move(str(subdir), str(target))
                            print(f'  [✓] Flattened: {rel_path} -> {target.relative_to(CORE)}')
                            moved += 1
                        except Exception as e:
                            print(f'  [X] Failed: {subdir.name} - {e}')
    print('\n[*] Cleaning empty directories...')
    for layer in ANNEXED_LAYERS:
        layer_path: Any = CORE / layer
        if not layer_path.exists():
            continue
        for root, dirs, files in os.walk(layer_path, topdown=False):
            for dir_name in dirs:
                dir_path: Any = Path(root) / dir_name
                try:
                    if not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        print(f'  [✓] Removed empty: {dir_path.relative_to(CORE)}')
                except:
                    pass
    print(f'\n[OK] FLATTENING COMPLETE. {moved} files moved to depth-{REQUIRED_DEPTH}.')
if __name__ == '__main__':
    flatten_annexed()
