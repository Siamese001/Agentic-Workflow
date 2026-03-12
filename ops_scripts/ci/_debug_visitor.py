"""Debug AST visitor for mixed list in AnnAssign."""
import sys, ast
# guardian: allow-global-mutation
sys.path.insert(0, '.')
from pathlib import Path
from ops_scripts.ci._fix_hardcoded_ssot_literals import _collect_safe_positions
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
content = Path('agentic_core/L0_routing/utils/scorched_earth_merge_util.py').read_text(encoding='utf-8')
safe_positions = _collect_safe_positions(content)
print(f'Safe positions: {len(safe_positions)}')
for pos in sorted(safe_positions):
    if pos[0] == 23:
        print(f'  Line 23, col {pos[1]} is safe')
tree = ast.parse(content)
for node in ast.walk(tree):
    if isinstance(node, ast.Constant) and node.value == AGENTIC_CORE_DIR:
        print(f'"agentic_core" at line {node.lineno}, col {node.col_offset}')
        print(f'  Is safe: {(node.lineno, node.col_offset) in safe_positions}')
