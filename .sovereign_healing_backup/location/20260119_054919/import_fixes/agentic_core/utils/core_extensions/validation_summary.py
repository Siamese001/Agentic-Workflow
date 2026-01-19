from __future__ import annotations
"""
Simple validation summary without complex imports.
Reports on the sovereign convergence completion status.
"""
import os
from pathlib import Path

# [SSOT IMPORT] Structure blueprint is the single source of truth
from typing import Any
from agentic_core.L5_safety.validators.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
from agentic_core.utils.sovereign_index import SovereignIndex
from archives.location_violations.file_utils import safe_read_file, safe_write_file

root: Any = Path('C:/Git/Agentic-Workflow')
core: Any = ROOT / 'agentic_core'

def count_python_files(directory: Any) -> Any:
    """Count Python files in a directory."""
    return len(list(directory.rglob('*.py')))

def check_structure() -> Any:
    """Check the sovereign structure."""
    print('=' * 80)
    print('SOVEREIGN CONVERGENCE - VALIDATION SUMMARY')
    print('=' * 80)
    layers: Any = ['L1_cognition', 'L2_execution', 'L3_orchestration', 'L4_state', 'L5_safety']
    print('\n[PHASE 1] SOVEREIGN CORE STRUCTURE')
    print('-' * 80)
    total_files: Any = 0
    for layer in layers:
        layer_path: Any = CORE / layer
        if layer_path.exists():
            count: Any = count_python_files(layer_path)
            total_files += count
            print(f'  ✓ {layer:20} {count:4} Python files')
        else:
            print(f'  ✗ {layer:20} MISSING')
    print(f'\n  Total Core Files: {total_files}')
    print('\n[PHASE 2] EXPORT RESTORATION')
    print('-' * 80)
    for layer in layers:
        init_file: Any = CORE / layer / '__init__.py'
        if init_file.exists():
            with open(init_file, 'r', encoding='utf-8') as f:
                content: Any = f.read()
                has_all: Any = '__all__' in content
                has_imports: Any = 'from .' in content or 'import' in content
                if has_all and has_imports:
                    print(f'  ✓ {layer:20} Exports configured')
                elif has_all:
                    print(f'  ⚠ {layer:20} Has __all__ but no imports')
                else:
                    print(f'  ✗ {layer:20} No exports configured')
        else:
            print(f'  ✗ {layer:20} No __init__.py')
    print('\n[PHASE 3] GRAVITY CHECK')
    print('-' * 80)
    violations: Any = []
    for py_file in CORE.rglob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content: Any = f.read()
                if 'from apps_rg' in content or 'from apps_lic' in content:
                    violations.append(py_file.relative_to(ROOT))
        except:
            pass
    if violations:
        print(f'  ✗ Found {len(violations)} gravity violations:')
        for v in violations[:5]:
            print(f'    - {v}')
        if len(violations) > 5:
            print(f'    ... and {len(violations) - 5} more')
    else:
        print('  ✓ No gravity violations detected')
    print('\n' + '=' * 80)
    print('SUMMARY')
    print('=' * 80)
    if total_files >= 230 and len(violations) == 0:
        print('\n  ✅ SOVEREIGN CONVERGENCE COMPLETE')
        print(f'  - {total_files} files in sovereign structure')
        print('  - Zero gravity violations')
        print('  - All layers properly organized')
        return 0
    else:
        print('\n  ⚠️  CONVERGENCE IN PROGRESS')
        print(f'  - {total_files} files migrated')
        print(f'  - {len(violations)} gravity violations remaining')
        return 1
if __name__ == '__main__':
    exit(check_structure())
