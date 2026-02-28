"""
Determinism Serialization Checker

AST-based static analysis to ensure deterministic serialization in replay/storage modules.
Enforces invariants about JSON serialization and timestamp handling.
"""

from __future__ import annotations

import ast
from pathlib import Path


class DeterminismVisitor(ast.NodeVisitor):
    """AST visitor to detect non-deterministic serialization patterns."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.violations: list[tuple[int, str, str]] = []  # (lineno, rule_id, snippet)
        self.in_serialization_function = False
        self.current_function = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track function context."""
        old_function = self.current_function
        old_in_serialization = self.in_serialization_function
        self.current_function = node.name

        # Check if this is a serialization-related function
        serialization_functions = {
            "record_to_json",
            "record_from_json",
            "serialize",
            "deserialize",
            "to_json",
            "from_json",
            "save",
            "load",
            "write",
            "read",
            "serialize_with_timestamp",
        }
        self.in_serialization_function = node.name in serialization_functions

        self.generic_visit(node)

        # Restore state
        self.in_serialization_function = old_in_serialization
        self.current_function = old_function

    def visit_Call(self, node: ast.Call) -> None:
        """Check function calls for non-deterministic patterns."""
        # Check json.dumps calls
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "json":
                if node.func.attr == "dumps":
                    # Check for sort_keys=True
                    has_sort_keys = False
                    for kw in node.keywords:
                        if kw.arg == "sort_keys" and isinstance(kw.value, ast.Constant):
                            if kw.value.value is True:
                                has_sort_keys = True
                                break

                    if not has_sort_keys:
                        snippet = "json.dumps(...)"
                        self.violations.append((node.lineno, "JSON_NO_SORT_KEYS", snippet))

        # Check datetime.now() and time.time() in serialization contexts
        if self.in_serialization_function:
            if isinstance(node.func, ast.Attribute):
                # datetime.now()
                if node.func.attr == "now":
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "datetime":
                        snippet = "datetime.now()"
                        self.violations.append((node.lineno, "DATETIME_NOW", snippet))

                # time.time()
                if node.func.attr == "time":
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "time":
                        snippet = "time.time()"
                        self.violations.append((node.lineno, "TIME_TIME", snippet))

        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Check for imports of non-deterministic modules."""
        for alias in node.names:
            if alias.name in ["time", "datetime"]:
                # Only flag if used in serialization context
                # This is a weak check, but better than nothing
                if self.in_serialization_function:
                    snippet = f"import {alias.name}"
                    self.violations.append((node.lineno, "IMPORT_NON_DETERMINISTIC", snippet))

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check for from-imports of non-deterministic modules."""
        if node.module in ["time", "datetime"]:
            if self.in_serialization_function:
                snippet = f"from {node.module} import ..."
                self.violations.append((node.lineno, "IMPORT_FROM_NON_DETERMINISTIC", snippet))

        self.generic_visit(node)


def scan_file_for_determinism(file_path: Path) -> list[tuple[int, str, str]]:
    """Scan a single file for non-deterministic serialization patterns.

    Args:
        file_path: Path to file to scan

    Returns:
        List of (lineno, rule_id, snippet) tuples
    """
    violations = []

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Parse AST
        tree = ast.parse(content, filename=str(file_path))
        visitor = DeterminismVisitor(file_path)
        visitor.visit(tree)
        violations.extend(visitor.violations)

    except SyntaxError as e:
        violations.append((e.lineno or 0, "DET_SYNTAX_ERROR", f"Syntax error: {e.msg}"))
    except Exception as e:  # guardian: allow-silent-swallower
        violations.append((0, "DET_SCAN_ERROR", f"Scan error: {e}"))

    return violations


def scan_repository_for_determinism(repo_root: Path) -> list[tuple[str, int, str, str]]:
    """Scan repository for non-deterministic serialization in replay/storage modules.

    Args:
        repo_root: Repository root path

    Returns:
        List of (file_path, lineno, rule_id, snippet) tuples, sorted deterministically
    """
    all_violations = []

    # Scan replay and storage modules specifically
    scan_patterns = [
        "agentic_core/L3_orchestration/replay/**/*.py",
        "agentic_core/L4_state/storage/**/*.py",
    ]

    for pattern in scan_patterns:
        for py_file in repo_root.glob(pattern):
            violations = scan_file_for_determinism(py_file)
            for lineno, rule_id, snippet in violations:
                rel_path = str(py_file.relative_to(repo_root))
                all_violations.append((rel_path, lineno, rule_id, snippet))

    # Sort deterministically
    all_violations.sort(key=lambda x: (x[0], x[1], x[2], x[3]))

    return all_violations


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "scan_file_for_determinism",
    "scan_repository_for_determinism",
]
