"""
Tooling Apps Boundary Guard

Ensures tooling modules (evidence runners, CI scripts) do not import apps_* runtime modules.
Tooling must remain pure - apps_* can only be referenced as strings/paths in INSPECTED_FILES.

Deterministic, pure read-only, exits nonzero on violations.
"""
import argparse
import ast
import subprocess
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR


class ToolingAppsBoundaryChecker:
    """Checker for tooling/apps_* boundary violations."""
    TOOLING_DIRS = ['tools/evidence', 'ops_scripts/ci', 'ops_scripts/hooks']
    FORBIDDEN_IMPORTS = [APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR]

    def __init__(self, repo_root: Path, staged_only: bool = False):
        """Initialize checker.

        Args:
            repo_root: Repository root path
            staged_only: If True, only check staged files (git diff --cached)
        """
        self.repo_root = repo_root
        self.staged_only = staged_only
        self.violations = []

    def check_file(self, filepath: Path) -> None:
        """Check a single Python file for apps_* imports.

        Args:
            filepath: Path to Python file to check
        """    # guardian: Syntax errors should be caught at parser level, not runtime
        try:
            content = filepath.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(filepath))
        except SyntaxError as e:
            self.violations.append(f'{filepath}: Syntax error at line {e.lineno}')
            return
        except Exception as e:
            raise
            self.violations.append(f'{filepath}: Could not parse: {e}')
            return
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(alias.name.startswith(prefix) for prefix in self.FORBIDDEN_IMPORTS):
                        self.violations.append(f'{filepath}:{node.lineno}: Forbidden import: import {alias.name}')
            elif isinstance(node, ast.ImportFrom):
                if node.module and any(node.module.startswith(prefix) for prefix in self.FORBIDDEN_IMPORTS):
                    self.violations.append(f'{filepath}:{node.lineno}: Forbidden import: from {node.module} import ...')

    def get_staged_files(self) -> list[Path]:
        """Get list of staged tooling files."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRT"],
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                check=True,
            )
            staged_files = []
            for line in result.stdout.splitlines():
                if not line.strip():
                    continue
                file_path = self.repo_root / line
                # Check if it's a Python file in a tooling directory
                if (file_path.suffix == '.py' and
                    any(str(file_path).startswith(str(self.repo_root / d)) for d in self.TOOLING_DIRS)):
                    staged_files.append(file_path)
            return staged_files
        except subprocess.CalledProcessError:
            return []

    def check(self) -> list[str]:
        """Check tooling files for boundary violations.

        Returns:
            List of violation messages
        """
        if self.staged_only:
            # Only check staged files
            for py_file in self.get_staged_files():
                if py_file.name.startswith('_'):
                    continue
                self.check_file(py_file)
        else:
            # Check all tooling files (original behavior)
            for tooling_dir in self.TOOLING_DIRS:
                tooling_path = self.repo_root / tooling_dir
                if not tooling_path.exists():
                    continue
                for py_file in tooling_path.rglob('*.py'):
                    if py_file.name.startswith('_'):
                        continue
                    self.check_file(py_file)
        return self.violations


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check tooling/apps_* boundary violations",
    )
    parser.add_argument(
        "--staged-only",
        action="store_true",
        help="Only check staged files (git diff --cached)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent.parent
    checker = ToolingAppsBoundaryChecker(repo_root, staged_only=args.staged_only)
    violations = checker.check()

    if violations:
        print(f'\nERROR: Tooling/apps_* boundary violations found: {len(violations)}')
        for violation in violations:
            print(f'  - {violation}')
        return 1
    else:
        mode = "staged" if args.staged_only else "all"
        print(f'\nOK: All tooling modules respect apps_* boundary ({mode} files checked)')
        return 0
if __name__ == '__main__':
    sys.exit(main())
