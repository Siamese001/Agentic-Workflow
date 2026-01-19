from __future__ import annotations
import re
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from pathlib import Path

# [SSOT IMPORT] Structure blueprint is the single source of truth
from typing import Any
from agentic_core.L5_safety.validators.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
from archives.location_violations.file_utils import safe_read_file, safe_write_file

root: Any = Path('C:/Git/Agentic-Workflow')
mission_runner: Any = ROOT / 'agentic_core/L3_orchestration/mission_runner.py'

def fix_mission_runner() -> Any:
    """Remove all scripts.CanonValidator imports from mission_runner.py"""
    print('[*] Fixing mission_runner.py gravity violations...')
    with open(mission_runner, 'r', encoding='utf-8') as f:
        lines: Any = f.readlines()
    new_lines: Any = []
    skip_until_blank: Any = False
    for i, line in enumerate(lines):
        if 'from scripts.CanonValidator' in line:
            if not skip_until_blank:
                new_lines.append('    # GRAVITY FIX: Removed all scripts.CanonValidator imports\n')
                new_lines.append('    # These agents need to be moved to agentic_core or refactored\n')
                skip_until_blank: Any = True
            continue
        if skip_until_blank and line.strip() == ')':
            continue
        if skip_until_blank and line.strip() == '':
            skip_until_blank: Any = False
        if 'TODO: Move' in line and 'to agentic_core' in line:
            continue
        if 'STRUCTURAL FIX:' in line:
            continue
        if line.strip().startswith('#') and 'from scripts.CanonValidator' in line:
            continue
        new_lines.append(line)
    with open(mission_runner, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f'  ✓ Removed all scripts imports from mission_runner.py')
    print(f'  Note: This file will need refactoring to work without these agents')
if __name__ == '__main__':
    fix_mission_runner()
