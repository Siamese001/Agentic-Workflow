#!/usr/bin/env python3
"""Targeted syntax fix for active test files only.

This script only fixes files in the main tests/ directory,
excluding archives and backup directories.
"""

import ast
import pathlib
import re


class TargetedSyntaxFixer:
    """Targeted fixer for syntax errors in active test files."""

    def __init__(self, repo_root: pathlib.Path):
        self.repo_root = repo_root
        self.tests_dir = repo_root / "tests"
        self.stats = {
            "total_files": 0,
            "syntax_errors_fixed": 0,
            "legacy_comments_removed": 0,
            "unmatched_parens_removed": 0,
            "indentation_fixed": 0,
            "files_with_errors": 0,
        }
        self.failed_files: list[tuple[str, str]] = []

    def fix_active_test_files(self) -> dict:
        """Fix syntax errors in active test files only."""
        # Only process files in tests/ directory, exclude archives
        test_files = []
        for pattern in ["test_*.py", "*/test_*.py"]:
            test_files.extend(self.tests_dir.rglob(pattern))

        # Filter out archive directories
        active_test_files = []
        for test_file in test_files:
            if "archive" not in str(test_file).lower():
                active_test_files.append(test_file)

        print(f"Found {len(active_test_files)} active test files to check...")

        for test_file in active_test_files:
            self.stats["total_files"] += 1
            if self.fix_file(test_file):
                self.stats["files_with_errors"] += 1

        return self.stats

    def fix_file(self, file_path: pathlib.Path) -> bool:
        """Fix syntax errors in a single file."""
        try:
            original_content = file_path.read_text(encoding="utf-8")
        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            self.failed_files.append((str(file_path), f"Read error: {e}"))
            return False

        # Check if file has syntax errors
        try:
            ast.parse(original_content)
            return False  # No syntax errors, skip
        except SyntaxError:
            pass  # File has syntax errors, needs fixing

        fixed_content = original_content
        changes_made = False

        # Apply fixes in order
        fixed_content = self._comprehensive_fix(fixed_content)
        changes_made = True

        # Validate the fix
        try:
            ast.parse(fixed_content)
            # If successful, write back
            file_path.write_text(fixed_content, encoding="utf-8")
            self.stats["syntax_errors_fixed"] += 1
            return True
        except SyntaxError as e:
            self.failed_files.append((str(file_path), f"Syntax error after fix: {e}"))
            return False

    def _comprehensive_fix(self, content: str) -> str:
        """Apply comprehensive syntax fixes."""
        lines = content.splitlines()
        fixed_lines = []

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                fixed_lines.append(line)
                i += 1
                continue

            # Remove legacy comment lines
            if re.match(r"^\s*#\s*#\s*MOVED:.*$", line):
                self.stats["legacy_comments_removed"] += 1
                i += 1
                continue

            # Remove lines that are just closing parentheses
            if re.match(r"^\s*\)\s*$", line):
                self.stats["unmatched_parens_removed"] += 1
                i += 1
                continue

            # Fix import statements at wrong level
            if stripped.startswith(("from ", "import ")) and any(
                prefix in stripped for prefix in ["agentic_core", "apps_", "system_learning"]
            ):
                # If it's at module level (no indentation), it's wrong
                if not line.startswith(" ") and not line.startswith("\t"):
                    # Look ahead to find the next test function
                    j = i + 1
                    while j < len(lines) and not re.match(r"^\s*def\s+test_\w+", lines[j]):
                        j += 1

                    if j < len(lines):
                        # Found a test function, move import there
                        next_line = lines[j]
                        indent_match = re.match(r"^(\s*)def\s+test_\w+", next_line)
                        if indent_match:
                            indent = indent_match.group(1)
                            # Add import with proper indentation
                            fixed_lines.append(f"{indent}    {stripped}")
                            self.stats["indentation_fixed"] += 1
                        else:
                            fixed_lines.append(line)
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

            i += 1

        return "\n".join(fixed_lines)

    def print_summary(self):
        """Print fixing summary."""
        print("\n" + "=" * 60)
        print("TARGETED SYNTAX FIX SUMMARY")
        print("=" * 60)
        print(f"Total files checked: {self.stats['total_files']}")
        print(f"Files with errors fixed: {self.stats['files_with_errors']}")
        print(f"Syntax errors fixed: {self.stats['syntax_errors_fixed']}")
        print(f"Legacy comments removed: {self.stats['legacy_comments_removed']}")
        print(f"Unmatched parentheses removed: {self.stats['unmatched_parens_removed']}")
        print(f"Indentation issues fixed: {self.stats['indentation_fixed']}")
        print(f"Failed files: {len(self.failed_files)}")

        if self.failed_files:
            print("\nFailed files (first 10):")
            for file_path, error in self.failed_files[:10]:
                print(f"  {file_path}: {error}")
            if len(self.failed_files) > 10:
                print(f"  ... and {len(self.failed_files) - 10} more")

        print("=" * 60)


def main():
    """Run targeted syntax fix."""
    repo_root = pathlib.Path(__file__).parent.parent

    print("🎯 TARGETED SYNTAX FIX - ACTIVE TEST FILES ONLY")
    print(f"Repository: {repo_root}")

    fixer = TargetedSyntaxFixer(repo_root)
    stats = fixer.fix_active_test_files()
    fixer.print_summary()

    # Validate the fix
    print("\n🔍 VALIDATING FIX...")
    test_files = []
    for pattern in ["test_*.py", "*/test_*.py"]:
        test_files.extend((repo_root / "tests").rglob(pattern))

    # Filter out archives
    active_test_files = [f for f in test_files if "archive" not in str(f).lower()]

    syntax_errors = 0

    for test_file in active_test_files:
        try:
            content = test_file.read_text(encoding="utf-8")
            ast.parse(content)
        except SyntaxError:
            syntax_errors += 1
        except UnicodeDecodeError:
            syntax_errors += 1

    print(f"Active test files: {len(active_test_files)}")
    print(f"Remaining syntax errors: {syntax_errors}")

    if syntax_errors == 0:
        print("✅ ALL ACTIVE SYNTAX ERRORS FIXED!")
    else:
        print(f"⚠️  {syntax_errors} active files still have syntax errors")

    return syntax_errors == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
