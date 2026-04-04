#!/usr/bin/env python3
"""Wave 15: Minimal Fix - Ultra-conservative approach.

This wave uses the most conservative approach possible,
only fixing the most obvious and safe issues.
"""

import ast
import pathlib
import re


class Wave15MinimalFix:
    """Wave 15: Ultra-conservative minimal fixes."""

    def __init__(self, repo_root: pathlib.Path):
        self.repo_root = repo_root
        self.tests_dir = repo_root / "tests"
        self.stats = {
            'total_files': 0,
            'files_processed': 0,
            'minimal_fixes': 0,
            'syntax_errors_fixed': 0,
            'failed_files': 0
        }
        self.failed_files: list[tuple[str, str]] = []

    def process_files(self) -> dict:
        """Process files with Wave 15 minimal fix."""
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

        print(f"Wave 15: Processing {len(active_test_files)} files with syntax errors...")

        for test_file in active_test_files:
            self.stats['total_files'] += 1
            if self.process_file(test_file):
                self.stats['files_processed'] += 1

        return self.stats

    def process_file(self, file_path: pathlib.Path) -> bool:
        """Process a single file with minimal fix."""
        try:
            original_content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.failed_files.append((str(file_path), f"Read error: {e}"))
            return False

        # Apply minimal fix
        fixed_content = self._minimal_fix(original_content)

        # Validate the fix
        try:
            ast.parse(fixed_content)
            file_path.write_text(fixed_content, encoding='utf-8')
            self.stats['syntax_errors_fixed'] += 1
            return True
        except SyntaxError as e:
            self.failed_files.append((str(file_path), f"Minimal fix failed: {e}"))
            return False

    def _minimal_fix(self, content: str) -> str:
        """Apply ultra-conservative minimal fixes."""
        lines = content.splitlines()
        fixed_lines = []

        for line in lines:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                fixed_lines.append(line)
                continue

            # Apply only the safest fixes
            fixed_line = self._apply_safest_fix(line, stripped)
            if fixed_line != line:
                self.stats['minimal_fixes'] += 1
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def _apply_safest_fix(self, line: str, stripped: str) -> str:
        """Apply only the safest possible fixes."""
        # Safest Fix 1: Remove lines that are just closing parentheses
        if re.match(r'^\s*\)\s*$', line):
            return ""

        # Safest Fix 2: Remove very specific legacy comments
        if re.match(r'^\s*#\s*#\s*MOVED:.*$', line):
            return ""

        # Safest Fix 3: Remove REMOVED comments
        if stripped.startswith('# REMOVED:'):
            return ""

        # Safest Fix 4: Comment out orphaned import content (safer than removing)
        if (not line.startswith(' ') and not line.startswith('\t') and
            (re.match(r'^_emit_[a-zA-Z_][a-zA-Z0-9_]*,?\s*$', stripped) or
             re.match(r'^emit_[a-zA-Z_][a-zA-Z0-9_]*,?\s*$', stripped))):
            return f"# {stripped}"

        return line

    def print_summary(self):
        """Print wave summary."""
        print("\n" + "="*60)
        print("WAVE 15: MINIMAL FIX SUMMARY")
        print("="*60)
        print(f"Total files checked: {self.stats['total_files']}")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Minimal fixes applied: {self.stats['minimal_fixes']}")
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
    """Run Wave 15 minimal fix."""
    repo_root = pathlib.Path(__file__).parent.parent

    print("🌊 WAVE 15: MINIMAL FIX")
    print(f"Repository: {repo_root}")

    fixer = Wave15MinimalFix(repo_root)
    stats = fixer.process_files()
    fixer.print_summary()

    return stats['syntax_errors_fixed'] > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
