from __future__ import annotations
import shutil
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from pathlib import Path
from typing import Any
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    safe_prefixed_filename,
    validate_no_duplicate_prefix,
)
root: Any = Path('C:/Git/Agentic-Workflow')
core: Any = ROOT / 'agentic_core'
obs_runtime: Any = CORE / 'observability/P1_core/runtime'

def flatten_observability_runtime() -> Any:
    """Brief description of functionality and purpose."""
    print('[*] FLATTENING observability/P1_core/runtime TO DEPTH-4...')
    moved: Any = 0
    if not OBS_RUNTIME.exists():
        print('[!] Runtime directory not found')
        return
    for py_file in OBS_RUNTIME.rglob('*.py'):
        if py_file.parent == OBS_RUNTIME:
            continue
        rel_path: Any = py_file.relative_to(OBS_RUNTIME)
        parts: Any = rel_path.parts[:-1]
        prefix: Any = '_'.join(parts)
        # [SAFEGUARD] Use SSOT function to prevent duplicate prefix sprawl
        new_name: Any = safe_prefixed_filename(prefix, py_file.name)
        
        # Validate no duplicate prefix was created
        has_dup, dup_msg = validate_no_duplicate_prefix(new_name)
        if has_dup:
            print(f'  [!] BLOCKED: {dup_msg}')
            continue
            
        target: Any = OBS_RUNTIME / new_name
        counter: Any = 1
        while target.exists():
            target: Any = OBS_RUNTIME / f'{prefix}_{counter}_{py_file.stem}{py_file.suffix}'
            counter += 1
        try:
            shutil.move(str(py_file), str(target))
            print(f'  [✓] {rel_path} -> {target.name}')
            moved += 1
        except Exception as e:
            print(f'  [X] Failed: {py_file.name} - {e}')
    print('\n[*] Cleaning empty directories...')
    for root, dirs, files in os.walk(OBS_RUNTIME, topdown=False):
        for dir_name in dirs:
            dir_path: Any = Path(root) / dir_name
            try:
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    print(f'  [✓] Removed: {dir_path.relative_to(CORE)}')
            except:
                pass
    print(f'\n[OK] FLATTENING COMPLETE. {moved} files moved to depth-4.')
if __name__ == '__main__':
    import os
    flatten_observability_runtime()
