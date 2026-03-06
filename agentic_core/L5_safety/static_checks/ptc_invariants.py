"""
PTC Invariants Scanner

Static analysis scanner for Programmatic Tool Calling invariants.
Enforces PTC-specific safety constraints and deterministic behavior.
"""

from __future__ import annotations

import ast
from pathlib import Path
from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)


class PTCInvariantVisitor(ast.NodeVisitor):
    """AST visitor to check PTC invariants."""

    def __init__(self, file_path: Path):
        """Initialize visitor with file path."""
        self.file_path = file_path
        self.violations = []
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
        return "# guardian: allow-ptc-exception" in self.current_line_content

    def visit_Call(self, node: ast.Call) -> None:
        """Check for shell=True usage in PTC tools."""
        # Check for subprocess calls with shell=True
        if isinstance(node.func, ast.Name) and node.func.id == "subprocess":
            for keyword in node.keywords:
                if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant):
                    if keyword.value.value is True:
                        if not self._check_allowlist():
                            self.violations.append(
                                (
                                    node.lineno,
                                    "PTC_SHELL_TRUE",
                                    "subprocess with shell=True not allowed in PTC tools",
                                )
                            )

        # Check for PowerShell in string literals within PTC directory
        if "ptc" in str(self.file_path).lower():
            if isinstance(node.func, ast.Attribute):
                # Check for run commands that might contain PowerShell
                if node.func.attr == "run":
                    for arg in node.args:
                        if isinstance(arg, ast.Str) or isinstance(arg, ast.Constant):
                            value = arg.value if hasattr(arg, "value") else arg.s
                            if isinstance(value, str):
                                if "pwsh" in value.lower() or "powershell" in value.lower():
                                    if not self._check_allowlist():
                                        self.violations.append(
                                            (
                                                node.lineno,
                                                "PTC_POWERSHELL_LITERAL",
                                                f"PowerShell literal detected: {value}",
                                            )
                                        )

        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Check ToolSpec args are sorted."""
        if "ptc" in str(self.file_path).lower():
            # Look for ToolSpec definitions
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and "spec" in target.id.lower():
                            # Check if this is a ToolSpec with args
                            if isinstance(item.value, ast.Call):
                                for keyword in item.value.keywords:
                                    if keyword.arg == "args" and isinstance(keyword.value, ast.Tuple):
                                        arg_names = []
                                        for elt in keyword.value.elts:
                                            if isinstance(elt, ast.Call):
                                                for kw in elt.keywords:
                                                    if kw.arg == "name":
                                                        if isinstance(kw.value, ast.Constant):
                                                            arg_names.append(kw.value.value)

                                        # Check if args are sorted
                                        if arg_names != sorted(arg_names):
                                            self.violations.append(
                                                (
                                                    node.lineno,
                                                    "PTC_UNSORTED_ARGS",
                                                    f"ToolSpec args not sorted: {arg_names}",
                                                )
                                            )

        self.generic_visit(node)


def scan_file_for_ptc_invariants(file_path: Path) -> list[tuple[int, str, str]]:
    """Scan a single file for PTC invariants violations.

    Args:
        file_path: Path to file to scan

    Returns:
        List of violations as (line, rule_id, description)
    """
    violations = []

    # Skip non-Python files
    if not file_path.suffix == ".py":
        return violations

    # Skip if not in PTC directory
    if "ptc" not in str(file_path).lower():
        return violations

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Parse AST
        tree = ast.parse(content, filename=str(file_path))
        visitor = PTCInvariantVisitor(file_path)
        visitor.visit(tree)
        violations.extend(visitor.violations)

    except SyntaxError as e:
        violations.append(
            (e.lineno or 0, "PTC_SYNTAX_ERROR", f"Syntax error: {e.msg}")
        )  # guardian: allow-silent-swallower
    except Exception as e:  # guardian: allow-silent-swallower
        violations.append((0, "PTC_SCAN_ERROR", f"Scan error: {e}"))  # guardian: allow-silent-swallower

    return violations


def scan_repository_for_ptc_invariants(repo_root: Path) -> list[tuple[str, int, str, str]]:
    """Scan repository for PTC invariants violations.

    Args:
        repo_root: Repository root path

    Returns:
        List of violations as (file_path, line, rule_id, description)
    """
    violations = []

    # Scan PTC directory
    ptc_dir = repo_root / AGENTIC_CORE_DIR / "L3_orchestration" / "ptc"
    if ptc_dir.exists():
        for file_path in ptc_dir.rglob("*.py"):
            file_violations = scan_file_for_ptc_invariants(file_path)
            for line, rule_id, description in file_violations:
                violations.append((str(file_path.relative_to(repo_root)), line, rule_id, description))

    # Sort violations deterministically
    violations.sort(key=lambda v: (v[0], v[1], v[2]))

    return violations
