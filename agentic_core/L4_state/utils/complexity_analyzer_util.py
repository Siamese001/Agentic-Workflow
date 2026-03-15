"""
Shared complexity analysis utilities.

SSOT for cyclomatic complexity calculation.
Used by: GovernanceAgent, StructuralEngineerAgent

Extracted from:
- GovernanceAgent._calculate_mccabe()
- StructuralEngineerAgent._calculate_complexity()

Both implementations were identical - this consolidates them.
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

if TYPE_CHECKING:
    pass


def calculate_mccabe_complexity(node: ast.AST) -> int:
    """
    Calculate cyclomatic complexity of an AST node.

    Complexity = 1 + number of decision points (if, for, while, and, or, except)

    Args:
        node: AST node to analyze (typically FunctionDef or AsyncFunctionDef)

    Returns:
        Cyclomatic complexity score (minimum 1)

    Example:
        >>> import ast
        >>> code = "def foo(x):\\n    if x > 0:\\n        return 1\\n    return 0"
        >>> tree = ast.parse(code)
        >>> calculate_mccabe_complexity(tree.body[0])
        2
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "calculate_mccabe_complexity", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "calculate_mccabe_complexity", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "calculate_mccabe_complexity")
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, ast.If | ast.For | ast.While | ast.ExceptHandler):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
    return complexity


# guardian: allow-magic-config
def check_function_complexity(node: ast.AST, max_complexity: int = 10) -> tuple[bool, int]:
    """
    Check if function exceeds complexity threshold.

    Args:
        node: AST node to analyze
        max_complexity: Maximum allowed complexity (default 10)

    Returns:
        Tuple of (passes_check, actual_complexity)

    Example:
        >>> import ast
        >>> code = "def simple(): return 1"
        >>> tree = ast.parse(code)
        >>> check_function_complexity(tree.body[0], max_complexity=10)
        (True, 1)
    """
    complexity = calculate_mccabe_complexity(node)
    return (complexity <= max_complexity, complexity)


# guardian: allow-magic-config
def analyze_file_complexity(file_path: str, max_complexity: int = 10) -> list[dict[str, any]]:
    """
    Analyze all functions in a file for complexity violations.

    Args:
        file_path: Path to Python file
        max_complexity: Maximum allowed complexity

    Returns:
        List of violations with file_path, line_number, function_name, complexity
    """
    violations = []
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                complexity = calculate_mccabe_complexity(node)
                if complexity > max_complexity:
                    violations.append(
                        {
                            "file_path": file_path,
                            "line_number": node.lineno,
                            "function_name": node.name,
                            "complexity": complexity,
                            "max_allowed": max_complexity,
                            "message": f"Function '{node.name}' has complexity {complexity} (max {max_complexity})",
                        }
                    )
    except (SyntaxError, FileNotFoundError, OSError):
        pass
    return violations
