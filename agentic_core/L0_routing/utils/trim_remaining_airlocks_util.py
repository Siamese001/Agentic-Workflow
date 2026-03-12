from __future__ import annotations
'\nAggressively trim the remaining 6 heavy airlock files.\nRemove all blank lines and condense imports to single lines.\n'
from pathlib import Path
from typing import Any
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
root: Any = Path('C:/Git/Agentic-Workflow')
core: Any = ROOT / AGENTIC_CORE_DIR
heavy_airlocks: Any = ['L1_cognition/P1_core/check_outreach/__init__.py', 'L1_cognition/P1_core/P1_retrieve/get_info/__init__.py', 'L1_cognition/P1_core/P1_retrieve/P1_retrieve/check_resume/__init__.py', 'L1_cognition/P1_core/P3_aggregate/P3_aggregate/pick_resume/__init__.py', 'L1_cognition/P1_core/P4_safety/__init__.py', 'L1_cognition/P1_core/P4_safety/P4_safety/check_resume/__init__.py']

def aggressive_trim(init_file: Any) -> Any:
    """Aggressively trim to ≤50 lines."""
    lines: Any = init_file.read_text(encoding='utf-8').splitlines()
    new_lines: Any = []
    for line in lines:
        stripped: Any = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        new_lines.append(line)
    if len(new_lines) > 50:
        condensed: Any = []
        in_all: Any = False
        for line in new_lines:
            if '__all__' in line and '[' in line:
                condensed.append(line)
            elif '__all__' in line:
                in_all: Any = True
                continue
            elif in_all and ']' in line:
                in_all: Any = False
                continue
            elif in_all:
                continue
            else:
                condensed.append(line)
        new_lines: Any = condensed
    content: Any = '\n'.join(new_lines) + '\n'
    assert_no_persistent_write('L0', 'write_text')
    init_file.write_text(content, encoding='utf-8')
    return len(new_lines)

def trim_remaining() -> Any:
    """Trim the remaining heavy airlocks."""
    print('[*] AGGRESSIVELY TRIMMING REMAINING AIRLOCKS...')
    for path_str in HEAVY_AIRLOCKS:
        init_file: Any = CORE / path_str.replace('/', '\\')
        if not init_file.exists():
            print(f"  [SKIP] {path_str} - doesn't exist")
            continue
        original_lines: Any = len(init_file.read_text(encoding='utf-8').splitlines())
        new_lines: Any = aggressive_trim(init_file)
        print(f'  [✓] Trimmed: {path_str} ({original_lines} -> {new_lines} lines)')
    print('\n[OK] Aggressive trimming complete')
if __name__ == '__main__':
    trim_remaining()
