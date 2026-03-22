#!/usr/bin/env python3
"""Find exact SOVEREIGN_TERRITORIES import/usage lines (not comments)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

files_to_check = [
    'agentic_core/L0_routing/scripts/run_guardian_hierarchy_compliance.py',
    'agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py',
    'agentic_core/L5_safety/reasoning/hierarchy_healer.py'
]

for f in files_to_check:
    filepath = ROOT / f
    content = filepath.read_text(encoding='utf-8', errors='ignore')

    lines = content.split('\n')
    print(f'\n{"="*80}')
    print(f'{f}')
    print("="*80)

    in_docstring = False
    for i, line in enumerate(lines, 1):
        # Track docstrings
        if '"""' in line:
            in_docstring = not in_docstring

        if 'SOVEREIGN_TERRITORIES' in line:
            stripped = line.strip()
            is_comment = stripped.startswith('#')

            if not is_comment and not in_docstring:
                print(f'Line {i}: {line}')
