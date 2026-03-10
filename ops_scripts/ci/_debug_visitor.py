#!/usr/bin/env python3
"""Debug AST visitor for mixed list in AnnAssign."""

import sys, ast
sys.path.insert(0, '.')
from pathlib import Path
from ops_scripts.ci._fix_hardcoded_ssot_literals import _collect_safe_positions

content = (Path('agentic_core/L0_routing/utils/scorched_earth_merge_util.py')
           .read_text(encoding='utf-8'))

safe_positions = _collect_safe_positions(content)

# Check if line 23, col 4 is marked safe
print(f'Safe positions: {len(safe_positions)}')
for pos in sorted(safe_positions):
    if pos[0] == 23:
        print(f'  Line 23, col {pos[1]} is safe')

# Parse and check the specific node
tree = ast.parse(content)
for node in ast.walk(tree):
    if isinstance(node, ast.Constant) and node.value == AGENTIC_CORE_DIR:
        print(f'"agentic_core" at line {node.lineno}, col {node.col_offset}')
        print(f'  Is safe: {(node.lineno, node.col_offset) in safe_positions}')
