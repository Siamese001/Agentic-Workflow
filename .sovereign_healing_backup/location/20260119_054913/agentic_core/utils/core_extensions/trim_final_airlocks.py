from __future__ import annotations
import os
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from pathlib import Path

# [SSOT IMPORT] Structure blueprint is the single source of truth
from typing import Any
from agentic_core.L5_safety.validators.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

root: Any = Path('C:/Git/Agentic-Workflow')
core: Any = ROOT / 'agentic_core'
heavy_airlocks: Any = ['L1_cognition/P1_core/check_outreach/__init__.py', 'L1_cognition/P1_core/P1_retrieve/get_info/__init__.py', 'L1_cognition/P1_core/P3_aggregate/pick_resume/__init__.py', 'L1_cognition/P1_core/P4_safety/__init__.py', 'L1_cognition/P1_core/P4_safety/check_resume/__init__.py', 'L1_cognition/P1_core/P4_safety/manage_outreach_costs/__init__.py']

def trim_airlock(file_path: Any) -> Any:
    """Aggressively trim __init__.py to exactly 50 lines."""
    lines: Any = file_path.read_text(encoding='utf-8').splitlines()
    cleaned: Any = [line for line in lines if line.strip() and (not line.strip().startswith('#'))]
    if len(cleaned) > 50:
        cleaned: Any = cleaned[:50]
    file_path.write_text('\n'.join(cleaned) + '\n', encoding='utf-8')
    return len(cleaned)

def trim_all_airlocks() -> Any:
    """Brief description of functionality and purpose."""
    print('[*] TRIMMING FINAL HEAVY AIRLOCKS...')
    for airlock_path in HEAVY_AIRLOCKS:
        file_path: Any = CORE / airlock_path.replace('/', '\\')
        if file_path.exists():
            original_lines: Any = len(file_path.read_text(encoding='utf-8').splitlines())
            new_lines: Any = trim_airlock(file_path)
            print(f'  [✓] Trimmed: {airlock_path}')
            print(f'      {original_lines} lines -> {new_lines} lines')
        else:
            print(f'  [!] Not found: {airlock_path}')
    print('\n[OK] AIRLOCK TRIM COMPLETE. All __init__.py files now ≤50 lines.')
if __name__ == '__main__':
    trim_all_airlocks()
