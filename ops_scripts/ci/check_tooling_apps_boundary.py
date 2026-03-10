#!/usr/bin/env python3
"""
Tooling Apps Boundary Guard

Ensures tooling modules (evidence runners, CI scripts) do not import apps_* runtime modules.
Tooling must remain pure - apps_* can only be referenced as strings/paths in INSPECTED_FILES.

Deterministic, pure read-only, exits nonzero on violations.
"""

import ast
import sys
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

class ToolingAppsBoundaryChecker:
    """Checker for tooling/apps_* boundary violations."""

    # Tooling directories that must not import apps_*
    TOOLING_DIRS = [
        "tools/evidence",
        "ops_scripts/ci",
        "ops_scripts/hooks",
    ]

    # Forbidden import prefixes
    FORBIDDEN_IMPORTS = [APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR]

    def __init__(self, repo_root: Path):
        """Initialize checker.

        Args:
            repo_root: Repository root path
        """
        self.repo_root = repo_root
        self.violations = []

    def check_file(self, filepath: Path) -> None:
        """Check a single Python file for apps_* imports.

        Args:
            filepath: Path to Python file to check
        """
        try:
            content = filepath.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(filepath))
        except SyntaxError as e:
            self.violations.append(f"{filepath}: Syntax error at line {e.lineno}")
            return
        except Exception as e:
            self.violations.append(f"{filepath}: Could not parse: {e}")
            return

        # Check all import statements
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(alias.name.startswith(prefix) for prefix in self.FORBIDDEN_IMPORTS):
                        self.violations.append(
                            f"{filepath}:{node.lineno}: Forbidden import: import {alias.name}"
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module and any(node.module.startswith(prefix) for prefix in self.FORBIDDEN_IMPORTS):
                    self.violations.append(
                        f"{filepath}:{node.lineno}: Forbidden import: from {node.module} import ..."
                    )

    def check(self) -> list[str]:
        """Check all tooling files for boundary violations.

        Returns:
            List of violation messages
        """
        for tooling_dir in self.TOOLING_DIRS:
            tooling_path = self.repo_root / tooling_dir
            if not tooling_path.exists():
                continue

            # Find all Python files in tooling directory
            for py_file in tooling_path.rglob("*.py"):
                if py_file.name.startswith("_"):
                    continue  # Skip private/test files
                self.check_file(py_file)

        return self.violations


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent.parent

    checker = ToolingAppsBoundaryChecker(repo_root)
    violations = checker.check()

    if violations:
        print(f"\nERROR: Tooling/apps_* boundary violations found: {len(violations)}")
        for violation in violations:
            print(f"  - {violation}")
        return 1
    else:
        print("\nOK: All tooling modules respect apps_* boundary")
        return 0


if __name__ == "__main__":
    sys.exit(main())
