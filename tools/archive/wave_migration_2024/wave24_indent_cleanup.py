#!/usr/bin/env python3
"""Wave 24: Indent Cleanup - Final indentation cleanup.

This wave focuses specifically on cleaning up all indentation issues
that are causing persistent syntax errors.
"""

import ast
import pathlib
import re


class Wave24IndentCleanup:
    """Wave 24: Final indentation cleanup."""

    def __init__(self, repo_root: pathlib.Path):
        self.repo_root = repo_root
        self.tests_dir = repo_root / "tests"
        self.stats = {
            'total_files': 0,
            'files_processed': 0,
            'indent_cleanups': 0,
            'syntax_errors_fixed': 0,
            'failed_files': 0
        }
        self.failed_files: list[tuple[str, str]] = []

    def process_files(self) -> dict:
        """Process files with Wave 24 indent cleanup."""
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

        print(f"Wave 24: Processing {len(active_test_files)} files with syntax errors...")

        for test_file in active_test_files:
            self.stats['total_files'] += 1
            if self.process_file(test_file):
                self.stats['files_processed'] += 1

        return self.stats

    def process_file(self, file_path: pathlib.Path) -> bool:
        """Process a single file with indent cleanup."""
        try:
            original_content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.failed_files.append((str(file_path), f"Read error: {e}"))
            return False

        # Apply indent cleanup
        fixed_content = self._cleanup_indentation(original_content)

        # Validate the fix
        try:
            ast.parse(fixed_content)
            file_path.write_text(fixed_content, encoding='utf-8')
            self.stats['syntax_errors_fixed'] += 1
            return True
        except SyntaxError as e:
            # Try aggressive cleanup
            aggressive_content = self._aggressive_indent_cleanup(original_content)
            try:
                ast.parse(aggressive_content)
                file_path.write_text(aggressive_content, encoding='utf-8')
                self.stats['syntax_errors_fixed'] += 1
                return True
            except SyntaxError as e2:
                self.failed_files.append((str(file_path), f"Indent cleanup failed: {e2}"))
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

            # Clean up indentation
            fixed_line = self._fix_indentation_line(line, stripped)
            if fixed_line != line:
                self.stats['indent_cleanups'] += 1
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def _fix_indentation_line(self, line: str, stripped: str) -> str:
        """Fix indentation for a specific line."""
        # Fix 1: Remove all indentation from problematic imports
        if (stripped.startswith(('from ', 'import ')) and
            any(prefix in stripped for prefix in ['agentic_core', 'apps_', 'system_learning'])):
            return stripped

        # Fix 2: Remove indentation from orphaned content
        if (not line.startswith(' ') and not line.startswith('\t') and
            (re.match(r'^_emit_[a-zA-Z_][a-zA-Z0-9_]*,?\s*$', stripped) or
             re.match(r'^emit_[a-zA-Z_][a-zA-Z0-9_]*,?\s*$', stripped) or
             re.match(r'^[A-Z_][A-Z0-9_]*,?\s*$', stripped))):
            return f"# {stripped}"

        # Fix 3: Remove unmatched parentheses
        if re.match(r'^\s*\)\s*$', line):
            return ""

        # Fix 4: Remove legacy comments
        if re.match(r'^\s*#\s*#\s*MOVED:.*$', line):
            return ""

        if stripped.startswith('# REMOVED:'):
            return ""

        return line

    def _aggressive_indent_cleanup(self, content: str) -> str:
        """Apply aggressive indentation cleanup."""
        lines = content.splitlines()
        fixed_lines = []

        for line in lines:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                fixed_lines.append(line)
                continue

            # Aggressively clean up all problematic lines
            if self._is_problematic_line(line, stripped):
                continue  # Skip problematic lines

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def _is_problematic_line(self, line: str, stripped: str) -> bool:
        """Check if line is problematic."""
        return (re.match(r'^\s*#\s*#\s*MOVED:.*$', line) or
                stripped.startswith('# REMOVED:') or
                re.match(r'^\s*\)\s*$', line) or
                (not line.startswith(' ') and not line.startswith('\t') and
                 (re.match(r'^_emit_[a-zA-Z_][a-zA-Z0-9_]*,?\s*$', stripped) or
                  re.match(r'^emit_[a-zA-Z_][a-zA-Z0-9_]*,?\s*$', stripped) or
                  re.match(r'^[A-Z_][A-Z0-9_]*,?\s*$', stripped))))

    def print_summary(self):
        """Print wave summary."""
        print("\n" + "="*60)
        print("WAVE 24: INDENT CLEANUP SUMMARY")
        print("="*60)
        print(f"Total files checked: {self.stats['total_files']}")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Indent cleanups: {self.stats['indent_cleanups']}")
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
    """Run Wave 24 indent cleanup."""
    repo_root = pathlib.Path(__file__).parent.parent

    print("🌊 WAVE 24: INDENT CLEANUP")
    print(f"Repository: {repo_root}")

    cleaner = Wave24IndentCleanup(repo_root)
    stats = cleaner.process_files()
    cleaner.print_summary()

    return stats['syntax_errors_fixed'] > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
