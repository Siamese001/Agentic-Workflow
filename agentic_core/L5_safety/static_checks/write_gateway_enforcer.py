"""
Write Gateway Enforcement Scanner

AST-based static analysis to detect direct file writes bypassing write_gateway.
Enforces that non-L2 layers use the write gateway for persistence operations.
"""

from __future__ import annotations

import ast
from pathlib import Path


class WriteGatewayVisitor(ast.NodeVisitor):
    """AST visitor to detect direct file writes."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.violations: list[tuple[int, str, str]] = []  # (lineno, rule_id, snippet)
        self.in_allowlisted_function = False
        self.current_line_content = ""

    def visit(self, node: ast.AST) -> None:
        """Override to track line content."""
        if hasattr(node, "lineno"):
            # Read the line content for allowlist checking
            try:
                with open(self.file_path, encoding="utf-8") as f:
                    lines = f.readlines()
                    if 0 <= node.lineno - 1 < len(lines):
                        self.current_line_content = lines[node.lineno - 1]
            except Exception:  # guardian: allow-silent-swallower
                pass
                self.current_line_content = ""

        super().visit(node)

    def _check_allowlist(self) -> bool:
        """Check if current line has allowlist comment."""
        return "# guardian: allow-direct-write" in self.current_line_content

    def visit_Call(self, node: ast.Call) -> None:
        """Check for direct file write calls."""
        if self._check_allowlist():
            self.generic_visit(node)
            return

        # Check open() with write modes
        if isinstance(node.func, ast.Name) and node.func.id == "open":
            if node.args:
                # Check mode argument
                mode_arg = None
                if len(node.args) >= 2:
                    mode_arg = node.args[1]
                else:
                    # Check keyword arguments
                    for kw in node.keywords:
                        if kw.arg == "mode":
                            mode_arg = kw.value
                            break

                if mode_arg and isinstance(mode_arg, ast.Constant):
                    if isinstance(mode_arg.value, str):
                        write_modes = {"w", "wb", "a", "ab", "w+", "wb+", "a+", "ab+"}
                        if any(mode_arg.value.startswith(mode) for mode in write_modes):
                            snippet = f'open(..., mode="{mode_arg.value}")'
                            self.violations.append((node.lineno, "DIRECT_OPEN_WRITE", snippet))

        # Check Path.write_text and Path.write_bytes
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ["write_text", "write_bytes"]:
                snippet = f"Path.{node.func.attr}(...)"
                self.violations.append((node.lineno, "DIRECT_PATH_WRITE", snippet))

        # Check json.dump with file handles
        if isinstance(node.func, ast.Name) and node.func.id == "json":
            if isinstance(node.func, ast.Name):
                # Look for json.dump calls
                if hasattr(node, "parent"):
                    # This would need more complex parent tracking in real implementation
                    pass

        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        """Check for 'with open(...)' patterns."""
        if self._check_allowlist():
            self.generic_visit(node)
            return

        for item in node.items:
            if isinstance(item.context_expr, ast.Call):
                if isinstance(item.context_expr.func, ast.Name) and item.context_expr.func.id == "open":
                    # Check if it's a write mode
                    mode_arg = None
                    if len(item.context_expr.args) >= 2:
                        mode_arg = item.context_expr.args[1]
                    else:
                        for kw in item.context_expr.keywords:
                            if kw.arg == "mode":
                                mode_arg = kw.value
                                break

                    if mode_arg and isinstance(mode_arg, ast.Constant):
                        if isinstance(mode_arg.value, str):
                            write_modes = {"w", "wb", "a", "ab", "w+", "wb+", "a+", "ab+"}
                            if any(mode_arg.value.startswith(mode) for mode in write_modes):
                                snippet = f'with open(..., mode="{mode_arg.value}")'
                                self.violations.append((node.lineno, "DIRECT_WITH_WRITE", snippet))

        self.generic_visit(node)


def scan_file_for_writes(file_path: Path) -> list[tuple[int, str, str]]:
    """Scan a single file for direct file writes.

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
        visitor = WriteGatewayVisitor(file_path)
        visitor.visit(tree)
        violations.extend(visitor.violations)

    except SyntaxError as e:
        violations.append((e.lineno or 0, "WRITE_SYNTAX_ERROR", f"Syntax error: {e.msg}"))
    except Exception as e:  # guardian: allow-silent-swallower
        violations.append((0, "WRITE_SCAN_ERROR", f"Scan error: {e}"))

    return violations


def scan_repository_for_writes(repo_root: Path) -> list[tuple[str, int, str, str]]:
    """Scan repository for direct file writes in agentic_core (excluding L2).

    Args:
        repo_root: Repository root path

    Returns:
        List of (file_path, lineno, rule_id, snippet) tuples, sorted deterministically
    """
    all_violations = []

    # Scan agentic_core/** excluding L2_execution/**
    agentic_core_path = repo_root / "agentic_core"
    if not agentic_core_path.exists():
        return []

    for py_file in agentic_core_path.rglob("*.py"):
        # Skip L2_execution directory
        if "L2_execution" in py_file.parts:
            continue

        violations = scan_file_for_writes(py_file)
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
    "scan_file_for_writes",
    "scan_repository_for_writes",
]
