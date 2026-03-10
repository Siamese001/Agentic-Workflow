#!/usr/bin/env python3
"""Debug why fixer misses mixed list cases."""

import sys, ast
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

sys.path.insert(0, '.')
from pathlib import Path

content = (Path('agentic_core/L0_routing/utils/scorched_earth_merge_util.py')
           .read_text(encoding='utf-8'))

tree = ast.parse(content)

# Find the specific list with "agentic_core"
for node in ast.walk(tree):
    if isinstance(node, ast.List):
        for elt in node.elts:
            if isinstance(elt, ast.Constant) and elt.value == AGENTIC_CORE_DIR:
                print(f'Found "agentic_core" at line {elt.lineno}, col {elt.col_offset}')
                print(f'  List elements: {[e.value if isinstance(e, ast.Constant) else type(e).__name__ for e in node.elts]}')
                
                # Check parent
                for parent in ast.walk(tree):
                    if hasattr(parent, 'elts') and node in parent.elts:
                        print(f'  Parent is {type(parent).__name__}')
                    elif hasattr(parent, 'value') and parent.value is node:
                        print(f'  Parent is {type(parent).__name__}')
                break
