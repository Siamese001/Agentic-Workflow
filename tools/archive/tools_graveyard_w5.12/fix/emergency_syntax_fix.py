#!/usr/bin/env python3
"""Emergency syntax fix for migrated test files.

Critical issue: 2,374 test files have syntax errors from migration.
This script fixes common issues:
1. Removes legacy "# # MOVED:" comments
2. Removes unmatched closing parentheses
3. Fixes indentation issues
"""

import ast
import pathlib
import re


class EmergencySyntaxFixer:
    """Emergency fixer for syntax errors in migrated test files."""

    def __init__(self, repo_root: pathlib.Path):
        self.repo_root = repo_root
        self.stats = {
            "total_files": 0,
            "syntax_errors_fixed": 0,
            "legacy_comments_removed": 0,
            "unmatched_parens_removed": 0,
            "indentation_fixed": 0,
            "files_with_errors": 0,
        }
        self.failed_files: list[tuple[str, str]] = []

    def fix_all_test_files(self) -> dict:
        """Fix syntax errors in all test files."""
        test_files = list(self.repo_root.rglob("test_*.py"))

        print(f"Found {len(test_files)} test files to check...")

        for test_file in test_files:
            self.stats["total_files"] += 1
            if self.fix_file(test_file):
                self.stats["files_with_errors"] += 1

        return self.stats

    def fix_file(self, file_path: pathlib.Path) -> bool:
        """Fix syntax errors in a single file."""
        try:
            original_content = file_path.read_text(encoding="utf-8")
        except Exception as e:
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

        # Fix 1: Remove legacy commented imports
        if self._remove_legacy_comments(fixed_content):
            changes_made = True
            fixed_content = self._remove_legacy_comments(fixed_content)
            self.stats["legacy_comments_removed"] += 1

        # Fix 2: Remove unmatched closing parentheses
        if self._remove_unmatched_parentheses(fixed_content):
            changes_made = True
            fixed_content = self._remove_unmatched_parentheses(fixed_content)
            self.stats["unmatched_parens_removed"] += 1

        # Fix 3: Fix indentation issues
        if self._fix_indentation_issues(fixed_content):
            changes_made = True
            fixed_content = self._fix_indentation_issues(fixed_content)
            self.stats["indentation_fixed"] += 1

        # Fix 4: Remove empty lines at the beginning
        fixed_content = self._fix_leading_empty_lines(fixed_content)

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

    def _remove_legacy_comments(self, content: str) -> str:
        """Remove '# # MOVED:' comments."""
        lines = content.splitlines()
        cleaned_lines = []

        for line in lines:
            # Remove lines that are just legacy comments
            if not re.match(r"^\s*#\s*#\s*MOVED:.*$", line):
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    def _remove_unmatched_parentheses(self, content: str) -> str:
        """Remove unmatched closing parentheses."""
        lines = content.splitlines()
        cleaned_lines = []

        for line in lines:
            # Remove lines that are just closing parentheses
            if not re.match(r"^\s*\)\s*$", line):
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    def _fix_indentation_issues(self, content: str) -> str:
        """Fix common indentation issues."""
        lines = content.splitlines()
        fixed_lines = []

        for line in lines:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                fixed_lines.append(line)
                continue

            # Check if this is an import statement at wrong indentation
            if stripped.startswith(("from ", "import ")) and any(
                prefix in stripped for prefix in ["agentic_core", "apps_", "system_learning"]
            ):
                # Check if it's at module level (no indentation)
                if not line.startswith(" ") and not line.startswith("\t"):
                    # This is likely a misplaced import, add proper indentation
                    fixed_lines.append("    " + stripped)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def _fix_leading_empty_lines(self, content: str) -> str:
        """Remove excessive empty lines at the beginning."""
        lines = content.splitlines()

        # Find first non-empty line
        first_content_line = 0
        for i, line in enumerate(lines):
            if line.strip():
                first_content_line = i
                break

        # Keep at most 2 empty lines at the beginning
        if first_content_line > 2:
            return "\n".join(lines[first_content_line - 2 :])

        return content

    def print_summary(self):
        """Print fixing summary."""
        print("\n" + "=" * 60)
        print("EMERGENCY SYNTAX FIX SUMMARY")
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
    """Run emergency syntax fix."""
    repo_root = pathlib.Path(__file__).parent.parent

    print("🚨 EMERGENCY SYNTAX FIX - STARTING")
    print(f"Repository: {repo_root}")

    fixer = EmergencySyntaxFixer(repo_root)
    stats = fixer.fix_all_test_files()
    fixer.print_summary()

    # Validate the fix
    print("\n🔍 VALIDATING FIX...")
    test_files = list(repo_root.rglob("test_*.py"))
    syntax_errors = 0

    for test_file in test_files:
        try:
            content = test_file.read_text(encoding="utf-8")
            ast.parse(content)
        except SyntaxError:
            syntax_errors += 1
        except UnicodeDecodeError:
            syntax_errors += 1

    print(f"Remaining syntax errors: {syntax_errors}")

    if syntax_errors == 0:
        print("✅ ALL SYNTAX ERRORS FIXED!")
    else:
        print(f"⚠️  {syntax_errors} files still have syntax errors")

    return syntax_errors == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
