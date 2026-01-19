from __future__ import annotations
import os
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import re
import shutil
from pathlib import Path

# [SSOT IMPORT] Structure blueprint is the single source of truth
from typing import Any
from agentic_core.L5_safety.validators.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
from agentic_core.utils.sovereign_index import SovereignIndex
from archives.location_violations.file_utils import safe_read_file, safe_write_file

root: Any = Path.cwd()
core: Any = ROOT / 'agentic_core'
migration_map: Any = {'agentic_core/engines': 'agentic_core/L2_execution/P3_engines', 'agentic_core/interfaces': 'agentic_core/L1_cognition/P1_interfaces', 'agentic_core/security': 'agentic_core/L5_safety/P4_security', 'agentic_core/agentic_workflow': 'agentic_core/L3_orchestration/P5_workflow'}

def flush_and_align() -> Any:
    """Brief description of functionality and purpose."""
    print('[*] STARTING SOVEREIGN ALIGNMENT V2 & CIRCULAR FLUSH...')
    for source, target in MIGRATION_MAP.items():
        src_path: Any = ROOT / source
        dest_path: Any = ROOT / target
        if src_path.exists():
            dest_path.mkdir(parents=True, exist_ok=True)
            for item in src_path.iterdir():
                dest_item: Any = dest_path / item.name
                if dest_item.exists():
                    print(f'      [!] Skipping {item.name} (already exists at destination)')
                    continue
                shutil.move(str(item), str(dest_item))
            try:
                src_path.rmdir()
                print(f'  [>] Migrated Drift: {source} -> {target}')
            except OSError:
                print(f'  [!] Could not remove {source} (not empty)')
        else:
            print(f'  [-] Skipped: {source} (not found)')
    print('\n[*] FLUSHING __init__.py FILES...')
    flush_count: Any = 0
    for init_file in CORE.rglob('__init__.py'):
        print(f'  [!] Flushing: {init_file.relative_to(ROOT)}')
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write(f'"""Sovereign Layer: {init_file.parent.name}"""\n')
        flush_count += 1
    print(f'  [OK] Flushed {flush_count} __init__.py files')
    print('\n[*] REWIRING IMPORTS...')
    rewire: Any = [('agentic_core\\.L5_safety\\.P1_red_team\\.analysis', 'agentic_core.L2_execution.tool_registry.analysis')]
    count: Any = 0
    for py_file in ROOT.rglob('*.py'):
        if any((p in str(py_file) for p in ['legacy_code', '.venv', 'data'])):
            continue
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content: Any = f.read()
            new_content: Any = content
            for old, new in rewire:
                new_content: Any = re.sub(old, new, new_content)
            if new_content != content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'  [✓] Rewired: {py_file.name}')
                count += 1
        except Exception as e:
            print(f'  [!] Failed to process {py_file}: {e}')
    print(f'\n[OK] CONVERGENCE V2 COMPLETE. {count} files rewired.')
    print("    [!] NEXT: Run 'python canon_validator_agentic_v2.py --target agentic_core'")
if __name__ == '__main__':
    flush_and_align()
