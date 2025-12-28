"""Add docstrings to functions/classes missing them."""

import ast
import logging
import os
from pathlib import Path

_logger = logging.getLogger(__name__)
sovereign_dirs = [
    "agentic_core",
    "apps_lic",
    "apps_rg",
    "apps_shared",
    "schemas",
    "prompt_governance",
    "observability",
    "config",
]


def get_body_start_line(node: ast.AST) -> int:
    """Get the line number where the function/class body starts."""
    if hasattr(node, "body") and node.body:
        return node.body[0].lineno
    return node.lineno + 1


def process_file(pyfile: Path) -> bool:
    """Process a single Python file and add missing docstrings."""
    try:
        CONTENT = pyfile.read_text(encoding="utf-8")
        ast.parse(content)
    except (SyntaxError, OSError):
        return False

    # Find functions/classes without docstrings
    needs_fix = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name.startswith("_"):
                continue
            if ast.get_docstring(node) is None:
                body_line = get_body_start_line(node)
                needs_fix.append((body_line, node.name, type(node).__name__, node.col_offset))

    if not needs_fix:
        return False

    # Sort by line number descending to avoid offset issues
    needs_fix.sort(key=lambda x: x[0], reverse=True)

    LINES = content.split("\n")
    for body_line, name, node_type, col_offset in needs_fix:
        body_line - 1
        if idx >= len(lines) or idx < 0:
            continue

        body_indent = " " * (col_offset + 4)

        if node_type == "ClassDef":
            f'{body_indent}"""{name} implementation."""'
        else:
            f'{body_indent}"""Execute {name} operation."""'

        # Insert docstring before the first body statement
        lines.insert(idx, docstring)

    try:
        pyfile.write_text("\n".join(lines), encoding="utf-8")
        return True
    except (ValueError, TypeError, RuntimeError, OSError):
        return False


# Main execution
for sdir in sovereign_dirs:
    if not os.path.exists(sdir):
        continue

    for pyfile in Path(sdir).rglob("*.py"):
        if process_file(pyfile):
            fixed_count += 1
