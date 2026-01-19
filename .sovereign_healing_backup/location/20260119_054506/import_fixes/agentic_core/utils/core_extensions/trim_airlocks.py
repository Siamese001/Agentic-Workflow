from __future__ import annotations
"""
Trim heavy airlock __init__.py files to meet 50-line limit.
Condenses verbose __all__ lists and removes blank lines.
"""
from pathlib import Path
from typing import Any

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
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

def trim_airlock(init_file: Any) -> Any:
    """Trim a single __init__.py file to ≤50 lines."""
    lines: Any = init_file.read_text(encoding='utf-8').splitlines()
    if len(lines) <= 50:
        return False
    new_lines: Any = []
    in_all: Any = False
    all_items: Any = []
    for line in lines:
        stripped: Any = line.strip()
        if not stripped:
            continue
        if '__all__' in line:
            in_all: Any = True
            continue
        if in_all:
            if ']' in line:
                in_all: Any = False
                continue
            items: Any = stripped.strip('\',"').split(',')
            all_items.extend([i.strip().strip('\'"') for i in items if i.strip()])
            continue
        new_lines.append(line)
    if all_items:
        important: Any = all_items[:8]
        new_lines.append(f'__all__ = {important}')
    content: Any = '\n'.join(new_lines) + '\n'
    init_file.write_text(content, encoding='utf-8')
    return True

def trim_all_airlocks() -> Any:
    """Trim all heavy airlock files."""
    print('[*] TRIMMING HEAVY AIRLOCKS...')
    trimmed: Any = 0
    for init_file in CORE.rglob('__init__.py'):
        lines: Any = init_file.read_text(encoding='utf-8').splitlines()
        if len(lines) > 50:
            if trim_airlock(init_file):
                new_lines: Any = len(init_file.read_text(encoding='utf-8').splitlines())
                print(f'  [✓] Trimmed: {init_file.relative_to(CORE)} ({len(lines)} -> {new_lines} lines)')
                trimmed += 1
    print(f'\n[OK] Trimmed {trimmed} airlock files')
if __name__ == '__main__':
    trim_all_airlocks()
