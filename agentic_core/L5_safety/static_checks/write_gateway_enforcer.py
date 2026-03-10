"""
Write Gateway Enforcement Scanner

AST-based static analysis to detect direct file writes bypassing write_gateway.
Enforces that non-L2 layers use the write gateway for persistence operations.
"""

from __future__ import annotations

import ast
from pathlib import Path


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class WriteGatewayVisitor(ast.NodeVisitor):
    """AST visitor to detect direct file writes."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.violations: list[tuple[int, str, str]] = []  # (lineno, rule_id, snippet)
        self.in_allowlisted_function = False
        self.current_line_content = ""
        self._with_flagged_lines: set[int] = set()

    def visit(self, node: ast.AST) -> None:
        """Override to track line content."""
        if hasattr(node, "lineno"):
            # Read the line content for allowlist checking
            try:
                with open(self.file_path, encoding="utf-8") as f:
                    lines = f.readlines()
                    if 0 <= node.lineno - 1 < len(lines):
                        self.current_line_content = lines[node.lineno - 1]
            except (OSError, UnicodeDecodeError, IndexError, AttributeError) as e:
                # File read errors are non-critical for this check
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

        # Check open() with write modes — skip if already flagged by visit_With
        if isinstance(node.func, ast.Name) and node.func.id == "open":
            if node.lineno in self._with_flagged_lines:
                self.generic_visit(node)
                return
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
                                # Mark the call's line so visit_Call doesn't double-report
                                self._with_flagged_lines.add(item.context_expr.lineno)

        self.generic_visit(node)


def scan_file_for_writes(file_path: Path) -> list[tuple[int, str, str]]:
    """Scan a single file for direct file writes.

    Args:
        file_path: Path to file to scan

    Returns:
        List of (lineno, rule_id, snippet) tuples
    """
    violations = []

    # Skip L2_execution directory (allowed to write)
    if "L2_execution" in str(file_path):
        return violations

    # Skip PTC store writes (via FileSystemStore only)
    if "ptc" in str(file_path).lower() and "tool_call_store.py" in str(file_path):
        return violations

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


# Directories where the UWG write-gateway contract is enforced.
# Legacy script/agent/reasoning dirs are excluded — they predate the UWG contract.
_WRITE_SCAN_ROOTS = [
    "agentic_core/L3_orchestration/replay",
    "agentic_core/L3_orchestration/arbitration",
    "agentic_core/L3_orchestration/ptc",
    "agentic_core/L4_state/storage",
]


def scan_repository_for_writes(repo_root: Path) -> list[tuple[str, int, str, str]]:
    """Scan governance-critical storage/replay directories for direct file writes.

    Only scans the directories where the UWG write-gateway contract is enforced.
    Legacy script, agent, and reasoning directories are excluded.

    Args:
        repo_root: Repository root path

    Returns:
        List of (file_path, lineno, rule_id, snippet) tuples, sorted deterministically
    """
    all_violations = []

    for scan_root in _WRITE_SCAN_ROOTS:
        scan_path = repo_root / scan_root
        if not scan_path.exists():
            continue

        for py_file in scan_path.rglob("*.py"):
            # Skip L2_execution (allowed to write directly)
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
