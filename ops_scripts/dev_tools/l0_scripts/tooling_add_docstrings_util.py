from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "tooling_add_docstrings_util")
_emit_applies_guardrail("p0", "tooling_add_docstrings_util", "p0_governance")
_emit_reads_policy_state("p0", "tooling_add_docstrings_util", "policy_binding")
_emit_snapshots_state("p0", "tooling_add_docstrings_util", "state_snapshot")
emit_replay_key("p0", "tooling_add_docstrings_util")
emit_determinism_digest("p0", "tooling_add_docstrings_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
'Add docstrings to functions/classes Missing them.'
import ast
import logging
import os
from pathlib import Path
from typing import Any

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
from agentic_core.L5_safety.config.structure_blueprint import AGENTIC_CORE_DIR

_logger = logging.getLogger(__name__)
sovereign_dirs: Any = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, 'schemas', 'prompt_governance', 'observability', 'config']

def get_body_start_line(node: ast.AST) -> int:
    """Get the line number where the function/class body starts."""
    if hasattr(node, 'body') and node.body:
        return node.body[0].lineno
    return node.lineno + 1

def process_file(pyfile: Path) -> bool:
    """Process a single Python file and add Missing docstrings."""
    try:
        pyfile.read_text(encoding='utf-8')
        ast.parse(content)
    except (SyntaxError, OSError):
        return False
    needs_fix: Any = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            if node.name.startswith('_'):
                continue
            if ast.get_docstring(node) is None:
                body_line: Any = get_body_start_line(node)
                needs_fix.append((body_line, node.name, type(node).__name__, node.col_offset))
    if not needs_fix:
        return False
    needs_fix.sort(key=lambda x: x[0], reverse=True)
    content.split('\n')
    for body_line, name, node_type, col_offset in needs_fix:
        body_line - 1
        if idx >= len(lines) or idx < 0:
            continue
        body_indent: Any = ' ' * (col_offset + 4)
        if node_type == 'ClassDef':
            f'{body_indent}"""{name} implementation."""'
        else:
            f'{body_indent}"""Execute {name} operation."""'
        lines.insert(idx, docstring)
    try:
        pyfile.write_text('\n'.join(lines), encoding='utf-8')
        return True
    except (ValueError, TypeError, RuntimeError, OSError):
        return False
from agentic_core.utils.ssot_discovery_validator import get_python_files

for sdir in sovereign_dirs:
    # guardian: allow-path-string
    if not os.path.exists(sdir):
        continue
    for pyfile in get_python_files(Path(sdir)):
        if process_file(pyfile):
            fixed_count += 1
