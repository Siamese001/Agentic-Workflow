#!/usr/bin/env python3
"""CI gate: Ban top-level app imports in test files.

Blocks new test files that use risky top-level imports from agentic_core, apps_*,
system_learning, or infrastructure modules. Enforces deferred import pattern
to prevent collection-phase crashes.
"""

import ast
import pathlib
import re
import sys

# Target import patterns to block
TARGET_IMPORT_PATTERNS = {
    r"^from\s+agentic_core\..*\s+import",
    r"^from\s+apps_\w+\..*\s+import",
    r"^from\s+system_learning\..*\s+import",
    r"^from\s+infrastructure\..*\s+import",
    r"^import\s+agentic_core\..+",
    r"^import\s+apps_\w+\..+",
    r"^import\s+system_learning\..+",
    r"^import\s+infrastructure\..+",
}

# Safe patterns (allowed at top level)
SAFE_PATTERNS = {
    r"^import\s+agentic_core$",
    r"^import\s+apps_\w+$",
    r"^import\s+system_learning$",
    r"^import\s+infrastructure$",
    r"^from\s+TYPE_CHECKING\s+import",
    r"^if\s+TYPE_CHECKING:",
}

# All test directories have been migrated in Waves 1-7


class ImportGateChecker:
    def __init__(self, repo_root: pathlib.Path):
        self.repo_root = repo_root
        self.violations = []
        self.stats = {
            "files_checked": 0,
            "violations": 0,
            "allowed": 0,
        }

    def check_directory(self, test_dir: str) -> dict:
        """Check all test files in a directory."""
        test_path = self.repo_root / test_dir
        if not test_path.exists():
            return self.stats

        test_files = list(test_path.rglob("test_*.py"))

        for test_file in test_files:
            self.check_file(test_file)

        return self.stats

    def check_file(self, file_path: pathlib.Path) -> bool:
        """Check a single test file for banned import patterns."""
        self.stats["files_checked"] += 1

        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except SyntaxError as e:
            self.violations.append(
                {
                    "file": str(file_path.relative_to(self.repo_root)),
                    "error": f"Syntax error: {e}",
                    "line": e.lineno or 0,
                }
            )
            self.stats["violations"] += 1
            return False
        except Exception as e:
            self.violations.append(
                {
                    "file": str(file_path.relative_to(self.repo_root)),
                    "error": f"Read error: {e}",
                    "line": 0,
                }
            )
            self.stats["violations"] += 1
            return False

        # Check if file is in migrated directories (all directories now migrated)
        relative_path = str(file_path.relative_to(self.repo_root))
        is_in_migrated_dir = True  # All directories have been migrated in Waves 1-7

        # Find top-level target imports
        violations = []
        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # Skip comments and empty lines
            if not line_stripped or line_stripped.startswith("#"):
                continue

            # Check if it's a banned pattern
            is_banned = False
            for banned_pattern in TARGET_IMPORT_PATTERNS:
                if re.match(banned_pattern, line):
                    is_banned = True
                    break

            if not is_banned:
                continue

            # Check if it's actually safe
            is_safe = False
            for safe_pattern in SAFE_PATTERNS:
                if re.match(safe_pattern, line):
                    is_safe = True
                    break

            if is_safe:
                continue

            # Check if it's inside TYPE_CHECKING block
            if self._is_inside_type_checking(lines, i - 1):
                continue

            # This is a violation
            violations.append(
                {
                    "line": i,
                    "content": line.strip(),
                    "reason": "Top-level app import (should be deferred to test function)",
                }
            )

        if violations:
            self.violations.append(
                {
                    "file": str(file_path.relative_to(self.repo_root)),
                    "violations": violations,
                }
            )
            self.stats["violations"] += len(violations)
            return False
        else:
            self.stats["allowed"] += 1
            return True

    def _is_inside_type_checking(self, lines: list[str], line_idx: int) -> bool:
        """Check if a line is inside a TYPE_CHECKING conditional block."""
        # Look backwards for TYPE_CHECKING pattern
        indent_level = len(lines[line_idx]) - len(lines[line_idx].lstrip())

        for i in range(line_idx, -1, -1):
            line = lines[i].strip()
            if "TYPE_CHECKING" in line:
                if line.startswith("if TYPE_CHECKING:") or line.startswith("from TYPE_CHECKING"):
                    return True
            # Stop if we hit a same-or-higher level dedent
            if i < line_idx:
                current_indent = len(lines[i]) - len(lines[i].lstrip())
                if current_indent < indent_level and lines[i].strip():
                    break

        return False

    def print_report(self):
        """Print violation report."""
        print("\n=== Import Gate Report ===")
        print(f"Files checked: {self.stats['files_checked']}")
        print(f"Files passed: {self.stats['allowed']}")
        print(f"Violations: {self.stats['violations']}")

        if self.violations:
            print("\n🚨 VIOLATIONS FOUND:")
            for violation in self.violations:
                if "error" in violation:
                    print(f"  {violation['file']}:{violation['line']} - {violation['error']}")
                else:
                    print(f"  {violation['file']}:")
                    for v in violation["violations"]:
                        print(f"    Line {v['line']}: {v['content']}")
                        print(f"      → {v['reason']}")
            print("\n💡 Fix: Move imports inside test functions or use pytest.importorskip()")
            return False
        else:
            print("✅ All files passed - no top-level app imports detected")
            return True


def main():
    if len(sys.argv) > 1:
        # Check specific directories
        dirs = sys.argv[1:]
    else:
        # Check all test directories
        test_root = pathlib.Path(__file__).parent.parent.parent / "tests"
        dirs = [d.name for d in test_root.iterdir() if d.is_dir() and not d.name.startswith("_")]

    repo_root = pathlib.Path(__file__).parent.parent.parent
    checker = ImportGateChecker(repo_root)

    for test_dir in dirs:
        # Ensure we're checking a test directory
        if not test_dir.startswith("tests/"):
            full_path = f"tests/{test_dir}"
        else:
            full_path = test_dir

        print(f"Checking {full_path}...")
        checker.check_directory(full_path)

    success = checker.print_report()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
