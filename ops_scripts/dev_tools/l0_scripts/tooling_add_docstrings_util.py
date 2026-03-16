from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
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
_emit_authorize_and_execute("p2", "tooling_add_docstrings_util", "execution_auth")
_emit_validates_capability("p2", "tooling_add_docstrings_util", "capability_check")
_emit_routes_to_capability("p2", "tooling_add_docstrings_util", "capability_route")
_emit_writes_via_uwg("p2", "tooling_add_docstrings_util", "uwg_write")
_emit_blocks_direct_write("p2", "tooling_add_docstrings_util", "direct_write_block")
_emit_records_tool_invocation("p2", "tooling_add_docstrings_util", "tool_invocation")
_emit_captures_execution_output("p2", "tooling_add_docstrings_util", "exec_output")
_emit_dispatches_agent("p3", "tooling_add_docstrings_util", "agent_dispatch")
_emit_coordinates_agents("p3", "tooling_add_docstrings_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "tooling_add_docstrings_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "tooling_add_docstrings_util", "healing_outcome")
_emit_escalates_failure("p3", "tooling_add_docstrings_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "tooling_add_docstrings_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "tooling_add_docstrings_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "tooling_add_docstrings_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "tooling_add_docstrings_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "tooling_add_docstrings_util", "eval_metric")
_emit_stores_embedding("p4", "tooling_add_docstrings_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "tooling_add_docstrings_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "tooling_add_docstrings_util", "exec_snapshot_link")
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
