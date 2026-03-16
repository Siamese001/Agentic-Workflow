"""Debug AST visitor for mixed list in AnnAssign."""
import ast
import sys

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "_debug_visitor")
_emit_applies_guardrail("p0", "_debug_visitor", "p0_governance")
_emit_reads_policy_state("p0", "_debug_visitor", "policy_binding")
_emit_snapshots_state("p0", "_debug_visitor", "state_snapshot")
emit_replay_key("p0", "_debug_visitor")
emit_determinism_digest("p0", "_debug_visitor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# guardian: allow-global-mutation
sys.path.insert(0, '.')
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)
from ops_scripts.ci._fix_hardcoded_ssot_literals import _collect_safe_positions

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
