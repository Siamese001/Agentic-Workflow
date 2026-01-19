from __future__ import annotations
"""Add docstrings to functions/classes Missing them."""
import ast
import logging
import os
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.validators.structure_blueprint import (
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
from archives.location_violations.sovereign_index import SovereignIndex
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
        CONTENT: Any = pyfile.read_text(encoding='utf-8')
        ast.parse(content)
    except (SyntaxError, OSError):
        return False
    needs_fix: Any = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name.startswith('_'):
                continue
            if ast.get_docstring(node) is None:
                body_line: Any = get_body_start_line(node)
                needs_fix.append((body_line, node.name, type(node).__name__, node.col_offset))
    if not needs_fix:
        return False
    needs_fix.sort(key=lambda x: x[0], reverse=True)
    LINES: Any = content.split('\n')
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
# Phase 6.7: Use ssot_discovery instead of rglob
from agentic_core.utils.ssot_discovery import get_python_files
for sdir in sovereign_dirs:
    if not os.path.exists(sdir):
        continue
    for pyfile in get_python_files(Path(sdir)):
        if process_file(pyfile):
            fixed_count += 1
