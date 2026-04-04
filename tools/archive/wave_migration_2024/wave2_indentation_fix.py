#!/usr/bin/env python3
"""Wave 2: Indentation Fix - Fix indentation issues from migration.

This wave focuses on fixing indentation problems that are causing
syntax errors after the basic cleanup.
"""

import ast
import pathlib


class Wave2IndentationFix:
    """Wave 2: Fix indentation issues."""

    def __init__(self, repo_root: pathlib.Path):
        self.repo_root = repo_root
        self.tests_dir = repo_root / "tests"
        self.stats = {
            'total_files': 0,
            'files_processed': 0,
            'indentation_fixed': 0,
            'syntax_errors_fixed': 0,
            'failed_files': 0
        }
        self.failed_files: list[tuple[str, str]] = []

    def process_files(self) -> dict:
        """Process files with Wave 2 indentation fix."""
        # Only process files in tests/ directory, exclude archives
        test_files = []
        for pattern in ["test_*.py", "*/test_*.py"]:
            test_files.extend(self.tests_dir.rglob(pattern))

        # Filter out archive directories
        active_test_files = []
        for test_file in test_files:
            if "archive" not in str(test_file).lower():
                active_test_files.append(test_file)

        print(f"Wave 2: Processing {len(active_test_files)} active test files...")

        for test_file in active_test_files:
            self.stats['total_files'] += 1
            if self.process_file(test_file):
                self.stats['files_processed'] += 1

        return self.stats

    def process_file(self, file_path: pathlib.Path) -> bool:
        """Process a single file with indentation fix."""
        try:
            original_content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.failed_files.append((str(file_path), f"Read error: {e}"))
            return False

        # Check if file has syntax errors
        try:
            ast.parse(original_content)
            return False  # No syntax errors, skip
        except SyntaxError:
            pass  # File has syntax errors, needs fixing

        # Apply indentation fix
        fixed_content = self._fix_indentation(original_content)

        # Validate the fix
        try:
            ast.parse(fixed_content)
            file_path.write_text(fixed_content, encoding='utf-8')
            self.stats['syntax_errors_fixed'] += 1
            return True
        except SyntaxError as e:
            self.failed_files.append((str(file_path), f"Syntax error after fix: {e}"))
            return False

    def _fix_indentation(self, content: str) -> str:
        """Fix indentation issues."""
        lines = content.splitlines()
        fixed_lines = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                fixed_lines.append(line)
                continue

            # Fix unexpected indent issues
            if self._has_unexpected_indent(line, stripped, lines, i):
                fixed_line = self._fix_line_indentation(line, stripped)
                if fixed_line != line:
                    self.stats['indentation_fixed'] += 1
                    fixed_lines.append(fixed_line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def _has_unexpected_indent(self, line: str, stripped: str, all_lines: list[str], current_idx: int) -> bool:
        """Check if line has unexpected indentation."""
        # Check for orphaned import content at wrong indentation
        if (stripped.startswith(('from ', 'import ')) and
            any(prefix in stripped for prefix in ['agentic_core', 'apps_', 'system_learning']) and
            (line.startswith(' ') or line.startswith('\t'))):

            # Check if this looks like orphaned content
            if current_idx > 0:
                prev_line = all_lines[current_idx - 1].strip()
                if not prev_line.startswith(('def ', 'class ', '@', 'if ', 'elif ', 'else:', 'for ', 'while ', 'with ', 'try:', 'except', 'finally:')):
                    return True

        return False

    def _fix_line_indentation(self, line: str, stripped: str) -> str:
        """Fix line indentation."""
        # For orphaned imports, remove indentation
        if stripped.startswith(('from ', 'import ')):
            return stripped

        return line

    def print_summary(self):
        """Print wave summary."""
        print("\n" + "="*60)
        print("WAVE 2: INDENTATION FIX SUMMARY")
        print("="*60)
        print(f"Total files checked: {self.stats['total_files']}")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Indentation issues fixed: {self.stats['indentation_fixed']}")
        print(f"Syntax errors fixed: {self.stats['syntax_errors_fixed']}")
        print(f"Failed files: {len(self.failed_files)}")

        if self.failed_files:
            print("\nFailed files (first 5):")
            for file_path, error in self.failed_files[:5]:
                print(f"  {file_path}: {error}")
            if len(self.failed_files) > 5:
                print(f"  ... and {len(self.failed_files) - 5} more")

        print("="*60)


def main():
    """Run Wave 2 indentation fix."""
    repo_root = pathlib.Path(__file__).parent.parent

    print("🌊 WAVE 2: INDENTATION FIX")
    print(f"Repository: {repo_root}")

    fixer = Wave2IndentationFix(repo_root)
    stats = fixer.process_files()
    fixer.print_summary()

    return stats['syntax_errors_fixed'] > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
