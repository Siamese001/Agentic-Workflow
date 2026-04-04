#!/usr/bin/env python3
"""Wave 8: Indentation Cleanup - Fix all indentation issues.

This wave focuses on fixing indentation problems that are causing
"unexpected indent" errors.
"""

import ast
import pathlib


class Wave8IndentationCleanup:
    """Wave 8: Fix indentation issues."""

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
        """Process files with Wave 8 indentation cleanup."""
        # Only process files in tests/ directory, exclude archives
        test_files = []
        for pattern in ["test_*.py", "*/test_*.py"]:
            test_files.extend(self.tests_dir.rglob(pattern))

        # Filter out archive directories and already valid files
        active_test_files = []
        for test_file in test_files:
            if "archive" not in str(test_file).lower():
                # Check if file has syntax errors
                try:
                    content = test_file.read_text(encoding='utf-8')
                    ast.parse(content)
                    continue  # Skip valid files
                except SyntaxError:
                    active_test_files.append(test_file)
                except UnicodeDecodeError:
                    continue

        print(f"Wave 8: Processing {len(active_test_files)} files with syntax errors...")

        for test_file in active_test_files:
            self.stats['total_files'] += 1
            if self.process_file(test_file):
                self.stats['files_processed'] += 1

        return self.stats

    def process_file(self, file_path: pathlib.Path) -> bool:
        """Process a single file with indentation cleanup."""
        try:
            original_content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.failed_files.append((str(file_path), f"Read error: {e}"))
            return False

        # Apply indentation cleanup
        fixed_content = self._cleanup_indentation(original_content)

        # Validate the fix
        try:
            ast.parse(fixed_content)
            file_path.write_text(fixed_content, encoding='utf-8')
            self.stats['syntax_errors_fixed'] += 1
            return True
        except SyntaxError as e:
            # Try aggressive cleanup
            aggressive_content = self._aggressive_indentation_cleanup(original_content)
            try:
                ast.parse(aggressive_content)
                file_path.write_text(aggressive_content, encoding='utf-8')
                self.stats['syntax_errors_fixed'] += 1
                return True
            except SyntaxError as e2:
                self.failed_files.append((str(file_path), f"Indentation cleanup failed: {e2}"))
                return False

    def _cleanup_indentation(self, content: str) -> str:
        """Clean up indentation issues."""
        lines = content.splitlines()
        fixed_lines = []

        for line in lines:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                fixed_lines.append(line)
                continue

            # Fix indentation issues
            fixed_line = self._fix_indentation_line(line, stripped)
            if fixed_line != line:
                self.stats['indentation_fixed'] += 1
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def _fix_indentation_line(self, line: str, stripped: str) -> str:
        """Fix indentation for a single line."""
        # Fix orphaned import content at wrong indentation
        if (stripped.startswith(('from ', 'import ')) and
            any(prefix in stripped for prefix in ['agentic_core', 'apps_', 'system_learning']) and
            (line.startswith(' ') or line.startswith('\t'))):

            # Check if this looks like orphaned content
            # If it's indented but should be at module level, remove indentation
            return stripped

        # Fix other indentation issues
        if self._has_unexpected_indent(line, stripped):
            # Remove excessive indentation
            return stripped

        return line

    def _has_unexpected_indent(self, line: str, stripped: str) -> bool:
        """Check if line has unexpected indentation."""
        # Check for common patterns that shouldn't be indented
        if (stripped.startswith(('from ', 'import ', 'def ', 'class ', '@', 'if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ', 'return ', 'yield ', 'raise ', 'break', 'continue', 'pass', 'global', 'nonlocal'))):
            # These should only be indented if they're inside another block
            # For now, we'll be conservative and only fix obvious cases
            if (line.startswith('    ') and  # 4 spaces or more
                stripped.startswith(('from ', 'import ')) and
                any(prefix in stripped for prefix in ['agentic_core', 'apps_', 'system_learning'])):
                return True

        return False

    def _aggressive_indentation_cleanup(self, content: str) -> str:
        """Apply aggressive indentation cleanup."""
        lines = content.splitlines()
        fixed_lines = []

        for line in lines:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                fixed_lines.append(line)
                continue

            # Remove all indentation for certain patterns
            if stripped.startswith(('from ', 'import ')):
                if any(prefix in stripped for prefix in ['agentic_core', 'apps_', 'system_learning']):
                    fixed_lines.append(stripped)  # Remove all indentation
                else:
                    fixed_lines.append(line)  # Keep original indentation for standard imports
            elif stripped.startswith(('def ', 'class ', '@')):
                fixed_lines.append(line)  # Keep function/class definitions as-is
            elif stripped.startswith(('if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ')):
                fixed_lines.append(line)  # Keep control structures as-is
            else:
                fixed_lines.append(line)  # Keep everything else as-is

        return '\n'.join(fixed_lines)

    def print_summary(self):
        """Print wave summary."""
        print("\n" + "="*60)
        print("WAVE 8: INDENTATION CLEANUP SUMMARY")
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
    """Run Wave 8 indentation cleanup."""
    repo_root = pathlib.Path(__file__).parent.parent

    print("🌊 WAVE 8: INDENTATION CLEANUP")
    print(f"Repository: {repo_root}")

    cleaner = Wave8IndentationCleanup(repo_root)
    stats = cleaner.process_files()
    cleaner.print_summary()

    return stats['syntax_errors_fixed'] > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
