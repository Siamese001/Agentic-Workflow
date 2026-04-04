#!/usr/bin/env python3
"""Wave 14: Parenthesis Fix - Fix unmatched parentheses.

This wave focuses on fixing "unmatched ')'" errors.
"""

import ast
import pathlib
import re


class Wave14ParenthesisFix:
    """Wave 14: Fix unmatched parentheses."""

    def __init__(self, repo_root: pathlib.Path):
        self.repo_root = repo_root
        self.tests_dir = repo_root / "tests"
        self.stats = {
            'total_files': 0,
            'files_processed': 0,
            'parentheses_fixed': 0,
            'syntax_errors_fixed': 0,
            'failed_files': 0
        }
        self.failed_files: list[tuple[str, str]] = []

    def process_files(self) -> dict:
        """Process files with Wave 14 parenthesis fix."""
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

        print(f"Wave 14: Processing {len(active_test_files)} files with syntax errors...")

        for test_file in active_test_files:
            self.stats['total_files'] += 1
            if self.process_file(test_file):
                self.stats['files_processed'] += 1

        return self.stats

    def process_file(self, file_path: pathlib.Path) -> bool:
        """Process a single file with parenthesis fix."""
        try:
            original_content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.failed_files.append((str(file_path), f"Read error: {e}"))
            return False

        # Apply parenthesis fix
        fixed_content = self._fix_parentheses(original_content)

        # Validate the fix
        try:
            ast.parse(fixed_content)
            file_path.write_text(fixed_content, encoding='utf-8')
            self.stats['syntax_errors_fixed'] += 1
            return True
        except SyntaxError as e:
            # Try aggressive fix
            aggressive_content = self._aggressive_parenthesis_fix(original_content)
            try:
                ast.parse(aggressive_content)
                file_path.write_text(aggressive_content, encoding='utf-8')
                self.stats['syntax_errors_fixed'] += 1
                return True
            except SyntaxError as e2:
                self.failed_files.append((str(file_path), f"Parenthesis fix failed: {e2}"))
                return False

    def _fix_parentheses(self, content: str) -> str:
        """Fix unmatched parentheses."""
        lines = content.splitlines()
        fixed_lines = []

        for line in lines:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                fixed_lines.append(line)
                continue

            # Fix unmatched parentheses
            fixed_line = self._fix_line_parentheses(line, stripped)
            if fixed_line != line:
                self.stats['parentheses_fixed'] += 1
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def _fix_line_parentheses(self, line: str, stripped: str) -> str:
        """Fix parentheses in a specific line."""
        # Remove unmatched closing parentheses
        if re.match(r'^\s*\)\s*$', line):
            return ""

        # Fix lines with unmatched parentheses at the end
        if stripped.endswith(')') and not self._has_matching_open_parenthesis(stripped):
            return stripped.rstrip(')')

        return line

    def _has_matching_open_parenthesis(self, line: str) -> bool:
        """Check if line has matching open parenthesis."""
        open_count = line.count('(')
        close_count = line.count(')')
        return open_count >= close_count

    def _aggressive_parenthesis_fix(self, content: str) -> str:
        """Apply aggressive parenthesis fix."""
        lines = content.splitlines()
        fixed_lines = []

        for line in lines:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                fixed_lines.append(line)
                continue

            # Aggressively remove all lines that are just closing parentheses
            if re.match(r'^\s*\)\s*$', line):
                continue

            # Remove trailing unmatched parentheses
            if stripped.endswith(')') and not self._has_matching_open_parenthesis(stripped):
                fixed_lines.append(stripped.rstrip(')'))
            else:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def print_summary(self):
        """Print wave summary."""
        print("\n" + "="*60)
        print("WAVE 14: PARENTHESIS FIX SUMMARY")
        print("="*60)
        print(f"Total files checked: {self.stats['total_files']}")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Parentheses fixed: {self.stats['parentheses_fixed']}")
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
    """Run Wave 14 parenthesis fix."""
    repo_root = pathlib.Path(__file__).parent.parent

    print("🌊 WAVE 14: PARENTHESIS FIX")
    print(f"Repository: {repo_root}")

    fixer = Wave14ParenthesisFix(repo_root)
    stats = fixer.process_files()
    fixer.print_summary()

    return stats['syntax_errors_fixed'] > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
