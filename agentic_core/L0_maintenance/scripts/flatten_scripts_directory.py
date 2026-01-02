from __future__ import annotations
"""
Flatten scripts directory to SSOT-compliant depth.
[SSOT] All depth requirements derived from SOVEREIGN_REGISTRY in structure_blueprint.py
"""
import os
import shutil
from pathlib import Path
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    safe_prefixed_filename,
    validate_no_duplicate_prefix,
)
from typing import Any
root: Any = Path('C:/Git/Agentic-Workflow')
core: Any = ROOT / 'agentic_core'
scripts_dir: Any = CORE / 'L0_maintenance/scripts'
required_depth: Any = SOVEREIGN_REGISTRY['agentic_core']['depth']

def flatten_scripts() -> Any:
    """Brief description of functionality and purpose."""
    print(f'[*] FLATTENING L0_maintenance/scripts TO DEPTH-{REQUIRED_DEPTH}...')
    moved: Any = 0
    if not SCRIPTS_DIR.exists():
        print('[!] Scripts directory not found')
        return
    for py_file in SCRIPTS_DIR.rglob('*.py'):
        rel_path: Any = py_file.relative_to(CORE)
        parts: Any = rel_path.parts
        if len(parts) > REQUIRED_DEPTH - 1:
            path_prefix: Any = '_'.join(parts[2:-1])
            # [SAFEGUARD] Use SSOT function to prevent duplicate prefix sprawl
            new_name: Any = safe_prefixed_filename(path_prefix, py_file.name)
            
            # Validate no duplicate prefix was created
            has_dup, dup_msg = validate_no_duplicate_prefix(new_name)
            if has_dup:
                print(f'  [!] BLOCKED: {dup_msg}')
                continue
                
            target: Any = SCRIPTS_DIR / new_name
            counter: Any = 1
            while target.exists():
                target: Any = SCRIPTS_DIR / f'{path_prefix}_{counter}_{py_file.stem}{py_file.suffix}'
                counter += 1
            try:
                shutil.move(str(py_file), str(target))
                print(f'  [✓] {rel_path} -> {target.relative_to(CORE)}')
                moved += 1
            except Exception as e:
                print(f'  [X] Failed: {py_file.name} - {e}')
    print('\n[*] Cleaning empty directories...')
    for root, dirs, files in os.walk(SCRIPTS_DIR, topdown=False):
        for dir_name in dirs:
            dir_path: Any = Path(root) / dir_name
            try:
                if not any(dir_path.iterdir()) and dir_path != SCRIPTS_DIR:
                    dir_path.rmdir()
                    print(f'  [✓] Removed: {dir_path.relative_to(CORE)}')
            except:
                pass
    print(f'\n[OK] FLATTENING COMPLETE. {moved} files moved to depth-{REQUIRED_DEPTH}.')
if __name__ == '__main__':
    flatten_scripts()
