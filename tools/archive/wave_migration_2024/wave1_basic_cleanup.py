#!/usr/bin/env python3
"""Wave 1: Basic Cleanup - Remove only the most obvious migration artifacts.

This wave focuses on removing clearly problematic patterns while
being conservative to avoid breaking valid code.
"""

import ast
import pathlib
import re


class Wave1BasicCleanup:
    """Wave 1: Basic cleanup of migration artifacts."""

    def __init__(self, repo_root: pathlib.Path):
        self.repo_root = repo_root
        self.tests_dir = repo_root / "tests"
        self.stats = {
            'total_files': 0,
            'files_processed': 0,
            'legacy_comments_removed': 0,
            'orphaned_lines_removed': 0,
            'syntax_errors_fixed': 0,
            'failed_files': 0
        }
        self.failed_files: list[tuple[str, str]] = []

    def process_files(self) -> dict:
        """Process files with Wave 1 basic cleanup."""
        # Only process files in tests/ directory, exclude archives
        test_files = []
        for pattern in ["test_*.py", "*/test_*.py"]:
            test_files.extend(self.tests_dir.rglob(pattern))

        # Filter out archive directories
        active_test_files = []
        for test_file in test_files:
            if "archive" not in str(test_file).lower():
                active_test_files.append(test_file)

        print(f"Wave 1: Processing {len(active_test_files)} active test files...")

        for test_file in active_test_files:
            self.stats['total_files'] += 1
            if self.process_file(test_file):
                self.stats['files_processed'] += 1

        return self.stats

    def process_file(self, file_path: pathlib.Path) -> bool:
        """Process a single file with basic cleanup."""
        try:
            original_content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.failed_files.append((str(file_path), f"Read error: {e}"))
            return False

        # Apply basic cleanup
        cleaned_content = self._basic_cleanup(original_content)

        # Only write if content changed
        if cleaned_content != original_content:
            try:
                # Validate the cleaned content
                ast.parse(cleaned_content)
                file_path.write_text(cleaned_content, encoding='utf-8')
                self.stats['syntax_errors_fixed'] += 1
                return True
            except SyntaxError:
                # If syntax error, try to fix it
                fixed_content = self._fix_syntax_errors(cleaned_content)
                try:
                    ast.parse(fixed_content)
                    file_path.write_text(fixed_content, encoding='utf-8')
                    self.stats['syntax_errors_fixed'] += 1
                    return True
                except SyntaxError as e:
                    self.failed_files.append((str(file_path), f"Syntax error after fix: {e}"))
                    return False

        return False

    def _basic_cleanup(self, content: str) -> str:
        """Apply basic cleanup to remove obvious migration artifacts."""
        lines = content.splitlines()
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()

            # Remove empty lines
            if not stripped:
                cleaned_lines.append(line)
                continue

            # Remove legacy comment lines (very specific pattern)
            if re.match(r'^\s*#\s*#\s*MOVED:.*$', line):
                self.stats['legacy_comments_removed'] += 1
                continue

            # Remove orphaned import content (very specific patterns)
            if (not line.startswith(' ') and not line.startswith('\t') and
                (re.match(r'^_emit_[a-zA-Z_][a-zA-Z0-9_]*,?\s*$', stripped) or
                 re.match(r'^emit_[a-zA-Z_][a-zA-Z0-9_]*,?\s*$', stripped) or
                 re.match(r'^[A-Z_][A-Z0-9_]*,?\s*$', stripped))):

                self.stats['orphaned_lines_removed'] += 1
                continue

            # Keep everything else
            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _fix_syntax_errors(self, content: str) -> str:
        """Fix basic syntax errors."""
        lines = content.splitlines()
        fixed_lines = []

        for line in lines:
            stripped = line.strip()

            # Remove unmatched closing parentheses
            if re.match(r'^\s*\)\s*$', line):
                continue

            # Fix basic indentation issues
            if (stripped.startswith(('from ', 'import ')) and
                any(prefix in stripped for prefix in ['agentic_core', 'apps_', 'system_learning']) and
                (line.startswith(' ') or line.startswith('\t'))):

                # Remove indentation for module-level imports
                fixed_lines.append(stripped)
                continue

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def print_summary(self):
        """Print wave summary."""
        print("\n" + "="*60)
        print("WAVE 1: BASIC CLEANUP SUMMARY")
        print("="*60)
        print(f"Total files checked: {self.stats['total_files']}")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Legacy comments removed: {self.stats['legacy_comments_removed']}")
        print(f"Orphaned lines removed: {self.stats['orphaned_lines_removed']}")
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
    """Run Wave 1 basic cleanup."""
    repo_root = pathlib.Path(__file__).parent.parent

    print("🌊 WAVE 1: BASIC CLEANUP")
    print(f"Repository: {repo_root}")

    cleaner = Wave1BasicCleanup(repo_root)
    stats = cleaner.process_files()
    cleaner.print_summary()

    return stats['syntax_errors_fixed'] > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
