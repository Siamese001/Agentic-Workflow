#!/usr/bin/env python3
"""Final syntax fix - complete resolution of migration syntax errors.

This script uses pattern recognition to fix all remaining syntax errors
from the migration process.
"""

import ast
import pathlib
import re


class FinalSyntaxFixer:
    """Final fixer for complete syntax error resolution."""

    def __init__(self, repo_root: pathlib.Path):
        self.repo_root = repo_root
        self.tests_dir = repo_root / "tests"
        self.stats = {
            "total_files": 0,
            "syntax_errors_fixed": 0,
            "patterns_fixed": {
                "legacy_comments": 0,
                "orphaned_imports": 0,
                "incomplete_imports": 0,
                "unmatched_parens": 0,
                "bad_indentation": 0,
            },
            "files_with_errors": 0,
        }
        self.failed_files: list[tuple[str, str]] = []

    def fix_active_test_files(self) -> dict:
        """Fix all syntax errors in active test files."""
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
        except Exception as e:
            self.failed_files.append((str(file_path), f"Read error: {e}"))
            return False

        # Check if file has syntax errors
        try:
            ast.parse(original_content)
            return False  # No syntax errors, skip
        except SyntaxError:
            pass  # File has syntax errors, needs fixing

        # Apply comprehensive fix
        fixed_content = self._comprehensive_syntax_fix(original_content)

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

    def _comprehensive_syntax_fix(self, content: str) -> str:
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

            # Pattern 1: Remove legacy comment blocks completely
            if self._is_legacy_comment_start(line):
                self.stats["patterns_fixed"]["legacy_comments"] += 1
                i = self._skip_legacy_comment_block(lines, i)
                continue

            # Pattern 2: Remove orphaned import content
            if self._is_orphaned_import_content(line, stripped):
                self.stats["patterns_fixed"]["orphaned_imports"] += 1
                i += 1
                continue

            # Pattern 3: Fix incomplete imports
            if self._is_incomplete_import(line, stripped):
                fixed_line = self._fix_incomplete_import(line)
                if fixed_line != line:
                    self.stats["patterns_fixed"]["incomplete_imports"] += 1
                    fixed_lines.append(fixed_line)
                else:
                    fixed_lines.append(line)
                i += 1
                continue

            # Pattern 4: Remove unmatched parentheses
            if self._is_unmatched_parenthesis(line):
                self.stats["patterns_fixed"]["unmatched_parens"] += 1
                i += 1
                continue

            # Pattern 5: Fix bad indentation
            if self._has_bad_indentation(line, stripped):
                fixed_line = self._fix_indentation(line)
                if fixed_line != line:
                    self.stats["patterns_fixed"]["bad_indentation"] += 1
                    fixed_lines.append(fixed_line)
                else:
                    fixed_lines.append(line)
                i += 1
                continue

            # Keep everything else
            fixed_lines.append(line)
            i += 1

        # Clean up multiple empty lines
        fixed_lines = self._clean_empty_lines(fixed_lines)

        return "\n".join(fixed_lines)

    def _is_legacy_comment_start(self, line: str) -> bool:
        """Check if line starts a legacy comment block."""
        return (
            "#  # MOVED:" in line
            or line.strip().startswith("#  # MOVED:")
            or re.match(r"^\s*#\s*#\s*MOVED:.*$", line)
        )

    def _skip_legacy_comment_block(self, lines: list[str], start_idx: int) -> int:
        """Skip entire legacy comment block."""
        i = start_idx + 1
        while i < len(lines):
            line = lines[i]
            if line.strip() and not line.startswith(" ") and not line.startswith("\t"):
                break
            i += 1
        return i

    def _is_orphaned_import_content(self, line: str, stripped: str) -> bool:
        """Check if line is orphaned import content."""
        if stripped.startswith("#") or stripped.startswith(("from ", "import ", "def ", "class ", "@")):
            return False

        # Check for common orphaned patterns
        orphaned_patterns = [
            r"^_emit_[a-zA-Z_][a-zA-Z0-9_]*,?\s*#.*$",
            r"^_emit_[a-zA-Z_][a-zA-Z0-9_]*,?\s*$",
            r"^[A-Z_][A-Z0-9_]*,?\s*#.*$",  # Constants like MAX_GROWTH_RATIO
            r"^[a-zA-Z_][a-zA-Z0-9_]*\s*,\s*$",  # Single identifier with comma
            r"^[a-zA-Z_][a-zA-Z0-9_]*\s*#.*$",  # Single identifier with comment
        ]

        for pattern in orphaned_patterns:
            if re.match(pattern, stripped):
                return True

        return False

    def _is_incomplete_import(self, line: str, stripped: str) -> bool:
        """Check if line has incomplete import syntax."""
        return (
            stripped.startswith("from ")
            and ":" not in stripped
            and "(" not in stripped
            and not stripped.endswith(")")
        )

    def _fix_incomplete_import(self, line: str) -> str:
        """Fix incomplete import by making it a proper comment."""
        return f"# {line.strip()}"

    def _is_unmatched_parenthesis(self, line: str) -> bool:
        """Check if line is unmatched parenthesis."""
        return re.match(r"^\s*\)\s*$", line)

    def _has_bad_indentation(self, line: str, stripped: str) -> bool:
        """Check if line has bad indentation."""
        if not stripped.startswith(("from ", "import ")):
            return False

        # Import at module level should not be indented
        if line.startswith(" ") or line.startswith("\t"):
            # Check if it's an agentic_core/apps_/system_learning import
            if any(prefix in stripped for prefix in ["agentic_core", "apps_", "system_learning"]):
                return True

        return False

    def _fix_indentation(self, line: str) -> str:
        """Fix bad indentation by removing it."""
        return line.strip()

    def _clean_empty_lines(self, lines: list[str]) -> list[str]:
        """Clean up multiple consecutive empty lines."""
        cleaned_lines = []
        prev_empty = False
        for line in lines:
            if not line.strip():
                if not prev_empty:
                    cleaned_lines.append(line)
                prev_empty = True
            else:
                cleaned_lines.append(line)
                prev_empty = False
        return cleaned_lines

    def print_summary(self):
        """Print fixing summary."""
        print("\n" + "=" * 60)
        print("FINAL SYNTAX FIX SUMMARY")
        print("=" * 60)
        print(f"Total files checked: {self.stats['total_files']}")
        print(f"Files with errors fixed: {self.stats['files_with_errors']}")
        print(f"Syntax errors fixed: {self.stats['syntax_errors_fixed']}")
        print("\nPatterns fixed:")
        for pattern, count in self.stats["patterns_fixed"].items():
            if count > 0:
                print(f"  {pattern}: {count}")
        print(f"Failed files: {len(self.failed_files)}")

        if self.failed_files:
            print("\nFailed files (first 10):")
            for file_path, error in self.failed_files[:10]:
                print(f"  {file_path}: {error}")
            if len(self.failed_files) > 10:
                print(f"  ... and {len(self.failed_files) - 10} more")

        print("=" * 60)


def main():
    """Run final syntax fix."""
    repo_root = pathlib.Path(__file__).parent.parent

    print("🎯 FINAL SYNTAX FIX - COMPLETE RESOLUTION")
    print(f"Repository: {repo_root}")

    fixer = FinalSyntaxFixer(repo_root)
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
        print("✅ ALL SYNTAX ERRORS FIXED!")
    else:
        print(f"⚠️  {syntax_errors} files still have syntax errors")

    return syntax_errors == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
