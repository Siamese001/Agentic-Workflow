#!/usr/bin/env python3
"""Wave 10: Simple Cleanup - Remove only obvious problematic lines.

This wave uses a very conservative approach to remove only clearly
problematic lines without touching valid code.
"""

import ast
import pathlib
import re


class Wave10SimpleCleanup:
    """Wave 10: Simple cleanup of obvious issues."""

    def __init__(self, repo_root: pathlib.Path):
        self.repo_root = repo_root
        self.tests_dir = repo_root / "tests"
        self.stats = {
            'total_files': 0,
            'files_processed': 0,
            'lines_removed': 0,
            'syntax_errors_fixed': 0,
            'failed_files': 0
        }
        self.failed_files: list[tuple[str, str]] = []

    def process_files(self) -> dict:
        """Process files with Wave 10 simple cleanup."""
        # Only process files with syntax errors
        test_files = []
        for pattern in ["test_*.py", "*/test_*.py"]:
            test_files.extend(self.tests_dir.rglob(pattern))

        # Filter out archives and already valid files
        active_test_files = []
        for test_file in test_files:
            if "archive" not in str(test_file).lower():
                try:
                    content = test_file.read_text(encoding='utf-8')
                    ast.parse(content)
                    continue  # Skip valid files
                except SyntaxError:
                    active_test_files.append(test_file)
                except UnicodeDecodeError:
                    continue

        print(f"Wave 10: Processing {len(active_test_files)} files with syntax errors...")

        for test_file in active_test_files:
            self.stats['total_files'] += 1
            if self.process_file(test_file):
                self.stats['files_processed'] += 1

        return self.stats

    def process_file(self, file_path: pathlib.Path) -> bool:
        """Process a single file with simple cleanup."""
        try:
            original_content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.failed_files.append((str(file_path), f"Read error: {e}"))
            return False

        # Apply simple cleanup
        cleaned_content = self._simple_cleanup(original_content)

        # Validate the fix
        try:
            ast.parse(cleaned_content)
            file_path.write_text(cleaned_content, encoding='utf-8')
            self.stats['syntax_errors_fixed'] += 1
            return True
        except SyntaxError as e:
            self.failed_files.append((str(file_path), f"Simple cleanup failed: {e}"))
            return False

    def _simple_cleanup(self, content: str) -> str:
        """Apply simple cleanup - remove only obvious problematic lines."""
        lines = content.splitlines()
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                cleaned_lines.append(line)
                continue

            # Remove ONLY clearly problematic lines
            if self._is_clearly_problematic(line, stripped):
                self.stats['lines_removed'] += 1
                continue

            # Keep everything else
            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _is_clearly_problematic(self, line: str, stripped: str) -> bool:
        """Check if line is clearly problematic (very conservative)."""
        # Only remove lines that are 100% problematic

        # Pattern 1: Unmatched closing parentheses (very obvious)
        if re.match(r'^\s*\)\s*$', line):
            return True

        # Pattern 2: Legacy migration comments (very specific)
        if re.match(r'^\s*#\s*#\s*MOVED:.*$', line):
            return True

        # Pattern 3: Removed migration comments (very specific)
        if stripped.startswith('# REMOVED:'):
            return True

        # Pattern 4: Orphaned import content (only if at module level and very specific)
        if (not line.startswith(' ') and not line.startswith('\t') and
            (re.match(r'^_emit_[a-zA-Z_][a-zA-Z0-9_]*,?\s*$', stripped) or
             re.match(r'^emit_[a-zA-Z_][a-zA-Z0-9_]*,?\s*$', stripped))):
            return True

        # Pattern 5: Constants at module level (very specific)
        if (not line.startswith(' ') and not line.startswith('\t') and
            re.match(r'^[A-Z_][A-Z0-9_]*,?\s*$', stripped)):
            return True

        return False  # Be conservative - keep everything else

    def print_summary(self):
        """Print wave summary."""
        print("\n" + "="*60)
        print("WAVE 10: SIMPLE CLEANUP SUMMARY")
        print("="*60)
        print(f"Total files checked: {self.stats['total_files']}")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Lines removed: {self.stats['lines_removed']}")
        print(f"Syntax errors fixed: {self.stats['syntax_errors_fixed']}")
        print(f"Failed files: {len(self.failed_files)}")

        if self.failed_files:
            print("\nFailed files (first 3):")
            for file_path, error in self.failed_files[:3]:
                print(f"  {file_path}: {error}")
            if len(self.failed_files) > 3:
                print(f"  ... and {len(self.failed_files) - 3} more")

        print("="*60)


def main():
    """Run Wave 10 simple cleanup."""
    repo_root = pathlib.Path(__file__).parent.parent

    print("🌊 WAVE 10: SIMPLE CLEANUP")
    print(f"Repository: {repo_root}")

    cleaner = Wave10SimpleCleanup(repo_root)
    stats = cleaner.process_files()
    cleaner.print_summary()

    return stats['syntax_errors_fixed'] > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
