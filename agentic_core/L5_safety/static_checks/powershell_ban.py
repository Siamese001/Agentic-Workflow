"""
PowerShell Prohibition Scanner

AST-based static analysis to detect PowerShell usage in the codebase.
Enforces the invariant that no runners/tools use PowerShell directly.
"""

from __future__ import annotations

import ast
from pathlib import Path


class PowerShellBanVisitor(ast.NodeVisitor):
    """AST visitor to detect PowerShell usage patterns."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.violations: list[tuple[int, str, str]] = []  # (lineno, rule_id, snippet)

    def visit_Call(self, node: ast.Call) -> None:
        """Check for subprocess calls with PowerShell - semantic callsite enforcement only."""
        # Check for subprocess.run, subprocess.call, etc. with PowerShell in argv0
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id == "subprocess":
                    # Check for PowerShell in first argument (argv list or string)
                    if node.args:
                        first_arg = node.args[0]

                        # Case 1: Single string argument (shell command)
                        if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                            cmd_lower = first_arg.value.lower()
                            if "pwsh" in cmd_lower or "powershell" in cmd_lower:
                                snippet = f"subprocess.{node.func.attr}(...{first_arg.value[:50]}...)"
                                self.violations.append((node.lineno, "PS_SUBPROCESS_ARGV0", snippet))

                        # Case 2: List argument (argv array) - check first element only
                        elif isinstance(first_arg, (ast.List, ast.Tuple)):
                            if first_arg.elts:
                                argv0 = first_arg.elts[0]
                                if isinstance(argv0, ast.Constant) and isinstance(argv0.value, str):
                                    argv0_lower = argv0.value.lower()
                                    # Only flag if argv0 itself is pwsh/powershell (not if it appears in args)
                                    if argv0_lower in ("pwsh", "powershell", "pwsh.exe", "powershell.exe"):
                                        snippet = f"subprocess.{node.func.attr}(['{argv0.value}', ...])"
                                        self.violations.append((node.lineno, "PS_SUBPROCESS_ARGV0", snippet))

        # Check for shell=True with subprocess calls (in tools/ directory)
        if "tools" in str(self.file_path):
            for keyword in node.keywords:
                if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant):
                    if keyword.value.value is True:
                        snippet = f"subprocess.{node.func.attr}(..., shell=True, ...)"
                        self.violations.append((node.lineno, "PS_SUBPROCESS_SHELL", snippet))

        self.generic_visit(node)


def scan_file_for_powershell(file_path: Path) -> list[tuple[int, str, str]]:
    """Scan a single file for PowerShell usage.

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
        visitor = PowerShellBanVisitor(file_path)
        visitor.visit(tree)
        violations.extend(visitor.violations)

    except SyntaxError as e:
        # Record syntax error as violation for manual review
        violations.append((e.lineno or 0, "PS_SYNTAX_ERROR", f"Syntax error: {e.msg}"))
    except Exception as e:  # guardian: allow-silent-swallower
        # Record other errors for manual review
        violations.append((0, "PS_SCAN_ERROR", f"Scan error: {e}"))

    return violations


def scan_repository_for_powershell(repo_root: Path) -> list[tuple[str, int, str, str]]:
    """Scan repository for PowerShell usage.

    Args:
        repo_root: Repository root path

    Returns:
        List of (file_path, lineno, rule_id, snippet) tuples, sorted deterministically
    """
    all_violations = []

    # Scan Python files in tools/ and docs/evidence/
    scan_dirs = ["tools", "docs/evidence"]

    for scan_dir in scan_dirs:
        dir_path = repo_root / scan_dir
        if not dir_path.exists():
            continue

        for py_file in dir_path.rglob("*.py"):
            violations = scan_file_for_powershell(py_file)
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
    "scan_file_for_powershell",
    "scan_repository_for_powershell",
]
