#!/usr/bin/env python3
"""
CI Gate: AST Collection Compliance Checker

Enforces Windsurf Constitutional Rule §4.3 - No grep/regex for structural logic.
Detects when test collection pipelines fall back to grep/regex instead of AST parsing.
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Set, Tuple, Union

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = REPO_ROOT / "tools"
CI_DIR = REPO_ROOT / "ops_scripts" / "ci"


class ASTComplianceChecker:
    """Checks for grep/regex violations in test collection pipelines."""

    # Forbidden patterns in test collection contexts (more precise)
    FORBIDDEN_PATTERNS = [
        r'pytest.*--collect-only.*\|.*grep',
        r'pytest.*--collect-only.*\|.*Select-String',
        r'pytest.*collect.*\|.*grep.*skip',
        r'pytest.*collect.*\|.*Select-String.*skip',
        r'grep.*pytest.*collect',
        r'Select-String.*pytest.*collect',
        r'rg.*pytest.*collect',
        r'findstr.*pytest.*collect',
        r'pytest.*collect.*2>&1.*\|.*grep',
        r'--collect-only.*\|.*grep',
        r'--collect-only.*\|.*Select-String',
    ]

    # Files that are allowed to use grep (non-structural contexts)
    ALLOWED_GREP_CONTEXTS = [
        "docs/",
        "README",
        "CHANGELOG",
        ".gitignore",
        "requirements.txt",
        "setup.py",
        "pyproject.toml",
    ]

    def __init__(self):
        self.violations: list[tuple[str, int, str]] = []

    def check_directory(self, directory: Path | str) -> None:
        """Check all Python files in a directory for violations."""
        if isinstance(directory, str):
            directory = Path(directory)
        for py_file in directory.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue

            self._check_file(py_file)

    def _should_skip_file(self, file_path: Path) -> bool:
        """Skip files that are allowed to use grep."""
        try:
            rel_path = file_path.relative_to(REPO_ROOT)
        except ValueError:
            # File is outside repo root, don't skip
            return False
        path_str = str(rel_path)

        # Skip allowed contexts
        for allowed in self.ALLOWED_GREP_CONTEXTS:
            if allowed in path_str:
                return True

        # Skip the compliance checker itself
        if file_path.name == "check_ast_collection_compliance.py":
            return True

        return False

    def _check_file(self, file_path: Path) -> None:
        """Check a single Python file for violations."""
        try:
            source = file_path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(file_path))
        except (SyntaxError, OSError):
            return

        # Check for forbidden patterns in source code
        self._check_patterns(file_path, source)

        # Check AST for subprocess calls with grep
        self._check_subprocess_calls(file_path, tree, source)

    def _check_patterns(self, file_path: Path, source: str) -> None:
        """Check source code for forbidden patterns."""
        try:
            rel_path = file_path.relative_to(REPO_ROOT)
            rel_path_str = str(rel_path)
        except ValueError:
            # File is outside repo root, use absolute path
            rel_path_str = str(file_path)

        # Skip pattern checking in the compliance checker itself (to avoid false positives)
        if file_path.name == "check_ast_collection_compliance.py":
            return

        for line_num, line in enumerate(source.splitlines(), 1):
            for pattern in self.FORBIDDEN_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    self.violations.append((
                        rel_path_str,
                        line_num,
                        f"Forbidden pattern detected: {pattern}"
                    ))

    def _check_subprocess_calls(self, file_path: Path, tree: ast.AST, source: str) -> None:
        """Check AST for subprocess calls that might use grep."""
        try:
            rel_path = file_path.relative_to(REPO_ROOT)
            rel_path_str = str(rel_path)
        except ValueError:
            # File is outside repo root, use absolute path
            rel_path_str = str(file_path)

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            # Check for subprocess.run, subprocess.call, etc.
            if self._is_subprocess_call(node):
                args = self._extract_subprocess_args(node)
                if args and self._args_contain_grep(args):
                    line_num = node.lineno if hasattr(node, 'lineno') else 0
                    self.violations.append((
                        rel_path_str,
                        line_num,
                        "Subprocess call with grep detected"
                    ))

    def _is_subprocess_call(self, node: ast.Call) -> bool:
        """Check if AST node is a subprocess call."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                return node.func.value.id == "subprocess"
            elif isinstance(node.func.value, ast.Attribute):
                # Handle subprocess.Popen.run style calls
                return node.func.value.attr == "subprocess"
        return False

    def _extract_subprocess_args(self, node: ast.Call) -> list[str]:
        """Extract command arguments from subprocess call."""
        args = []

        # Handle subprocess.run(["grep", ...])
        if (node.args and
            isinstance(node.args[0], (ast.List, ast.Tuple))):
            for elt in node.args[0].elts:
                if isinstance(elt, ast.Constant):
                    args.append(str(elt.value))

        # Handle subprocess.run("grep ...", shell=True)
        elif (node.args and
              isinstance(node.args[0], ast.Constant)):
            cmd_str = str(node.args[0].value)
            args = cmd_str.split()

        return args

    def _args_contain_grep(self, args: list[str]) -> bool:
        """Check if command arguments contain grep-like tools."""
        grep_tools = {"grep", "rg", "findstr", "Select-String", "egrep", "fgrep"}
        return any(arg in grep_tools for arg in args)

    def print_violations(self) -> None:
        """Print all violations found."""
        if not self.violations:
            print("✅ PASSED: No AST collection violations found.")
            return

        print(f"❌ FAILED: {len(self.violations)} AST collection violations found:")
        print()

        for file_path, line_num, message in self.violations:
            print(f"  {file_path}:{line_num} - {message}")

        print()
        print("Violations of Windsurf Constitutional Rule §4.3 detected!")
        print("Use tools/ast_test_collector.py for AST-based test collection.")

    def has_violations(self) -> bool:
        """Return True if any violations were found."""
        return len(self.violations) > 0


def main() -> int:
    """Main entry point for CI gate."""
    checker = ASTComplianceChecker()

    # Check tools directory
    print("Checking tools/ directory for AST compliance...")
    checker.check_directory(Path(TOOLS_DIR))

    # Check CI scripts directory
    print("Checking ops_scripts/ci/ directory for AST compliance...")
    checker.check_directory(Path(CI_DIR))

    # Print results
    checker.print_violations()

    return 1 if checker.has_violations() else 0


if __name__ == "__main__":
    sys.exit(main())
