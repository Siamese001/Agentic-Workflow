#!/usr/bin/env python3
"""Wave 11: Indent Fix - Fix only indentation issues.

This wave focuses specifically on fixing "unexpected indent" errors
by correcting indentation problems.
"""

import ast
import pathlib
import re


class Wave11IndentFix:
    """Wave 11: Fix indentation issues."""

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
        """Process files with Wave 11 indent fix."""
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

        print(f"Wave 11: Processing {len(active_test_files)} files with syntax errors...")

        for test_file in active_test_files:
            self.stats['total_files'] += 1
            if self.process_file(test_file):
                self.stats['files_processed'] += 1

        return self.stats

    def process_file(self, file_path: pathlib.Path) -> bool:
        """Process a single file with indent fix."""
        try:
            original_content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.failed_files.append((str(file_path), f"Read error: {e}"))
            return False

        # Apply indent fix
        fixed_content = self._fix_indentation(original_content)

        # Validate the fix
        try:
            ast.parse(fixed_content)
            file_path.write_text(fixed_content, encoding='utf-8')
            self.stats['syntax_errors_fixed'] += 1
            return True
        except SyntaxError as e:
            # Try more aggressive fix
            aggressive_content = self._aggressive_indent_fix(original_content)
            try:
                ast.parse(aggressive_content)
                file_path.write_text(aggressive_content, encoding='utf-8')
                self.stats['syntax_errors_fixed'] += 1
                return True
            except SyntaxError as e2:
                self.failed_files.append((str(file_path), f"Indent fix failed: {e2}"))
                return False

    def _fix_indentation(self, content: str) -> str:
        """Fix indentation issues."""
        lines = content.splitlines()
        fixed_lines = []

        for line in lines:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                fixed_lines.append(line)
                continue

            # Fix specific indentation issues
            fixed_line = self._fix_line_indentation(line, stripped)
            if fixed_line != line:
                self.stats['indentation_fixed'] += 1
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def _fix_line_indentation(self, line: str, stripped: str) -> str:
        """Fix indentation for a specific line."""
        # Fix 1: Remove indentation from orphaned imports at module level
        if (stripped.startswith(('from ', 'import ')) and
            any(prefix in stripped for prefix in ['agentic_core', 'apps_', 'system_learning']) and
            (line.startswith(' ') or line.startswith('\t'))):
            return stripped

        # Fix 2: Remove indentation from orphaned constants at module level
        if (not line.startswith(' ') and not line.startswith('\t') and
            re.match(r'^[A-Z_][A-Z0-9_]*,?\s*$', stripped)):
            return stripped

        # Fix 3: Remove indentation from orphaned emit functions at module level
        if (not line.startswith(' ') and not line.startswith('\t') and
            (re.match(r'^_emit_[a-zA-Z_][a-zA-Z0-9_]*,?\s*$', stripped) or
             re.match(r'^emit_[a-zA-Z_][a-zA-Z0-9_]*,?\s*$', stripped))):
            return stripped

        return line

    def _aggressive_indent_fix(self, content: str) -> str:
        """Apply aggressive indentation fix."""
        lines = content.splitlines()
        fixed_lines = []

        for line in lines:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                fixed_lines.append(line)
                continue

            # Aggressively fix all import statements
            if stripped.startswith(('from ', 'import ')):
                if any(prefix in stripped for prefix in ['agentic_core', 'apps_', 'system_learning']):
                    fixed_lines.append(stripped)  # Remove all indentation
                else:
                    fixed_lines.append(line)  # Keep standard imports as-is
            else:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def print_summary(self):
        """Print wave summary."""
        print("\n" + "="*60)
        print("WAVE 11: INDENT FIX SUMMARY")
        print("="*60)
        print(f"Total files checked: {self.stats['total_files']}")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Indentation fixed: {self.stats['indentation_fixed']}")
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
    """Run Wave 11 indent fix."""
    repo_root = pathlib.Path(__file__).parent.parent

    print("🌊 WAVE 11: INDENT FIX")
    print(f"Repository: {repo_root}")

    fixer = Wave11IndentFix(repo_root)
    stats = fixer.process_files()
    fixer.print_summary()

    return stats['syntax_errors_fixed'] > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
