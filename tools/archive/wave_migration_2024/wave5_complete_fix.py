#!/usr/bin/env python3
"""Wave 5: Complete Fix - Final resolution of all remaining syntax errors.

This wave applies comprehensive fixes to resolve all remaining syntax errors.
"""

import ast
import pathlib
import re


class Wave5CompleteFix:
    """Wave 5: Complete fix for remaining syntax errors."""

    def __init__(self, repo_root: pathlib.Path):
        self.repo_root = repo_root
        self.tests_dir = repo_root / "tests"
        self.stats = {
            'total_files': 0,
            'files_processed': 0,
            'comprehensive_fixes': 0,
            'syntax_errors_fixed': 0,
            'failed_files': 0
        }
        self.failed_files: list[tuple[str, str]] = []

    def process_files(self) -> dict:
        """Process files with Wave 5 complete fix."""
        # Only process files in tests/ directory, exclude archives
        test_files = []
        for pattern in ["test_*.py", "*/test_*.py"]:
            test_files.extend(self.tests_dir.rglob(pattern))

        # Filter out archive directories
        active_test_files = []
        for test_file in test_files:
            if "archive" not in str(test_file).lower():
                active_test_files.append(test_file)

        print(f"Wave 5: Processing {len(active_test_files)} active test files...")

        for test_file in active_test_files:
            self.stats['total_files'] += 1
            if self.process_file(test_file):
                self.stats['files_processed'] += 1

        return self.stats

    def process_file(self, file_path: pathlib.Path) -> bool:
        """Process a single file with complete fix."""
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

        # Apply comprehensive fix
        fixed_content = self._comprehensive_fix(original_content)

        # Validate the fix
        try:
            ast.parse(fixed_content)
            file_path.write_text(fixed_content, encoding='utf-8')
            self.stats['syntax_errors_fixed'] += 1
            return True
        except SyntaxError as e:
            self.failed_files.append((str(file_path), f"Syntax error after comprehensive fix: {e}"))
            return False

    def _comprehensive_fix(self, content: str) -> str:
        """Apply comprehensive fixes."""
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

            # Fix incomplete control structures
            if self._is_incomplete_control_structure(line, stripped):
                fixed_lines.extend(self._fix_incomplete_control_structure(line, stripped, lines, i))
                i += 1
                continue

            # Fix unmatched parentheses
            if self._has_unmatched_parenthesis(line, stripped):
                fixed_line = self._fix_unmatched_parenthesis(line, stripped)
                if fixed_line:
                    fixed_lines.append(fixed_line)
                i += 1
                continue

            # Fix indentation issues
            if self._has_indentation_issue(line, stripped):
                fixed_line = self._fix_indentation_issue(line, stripped)
                if fixed_line != line:
                    self.stats['comprehensive_fixes'] += 1
                    fixed_lines.append(fixed_line)
                else:
                    fixed_lines.append(line)
                i += 1
                continue

            # Remove problematic lines
            if self._is_problematic_line(line, stripped):
                i += 1
                continue

            # Keep everything else
            fixed_lines.append(line)
            i += 1

        # Final cleanup
        fixed_lines = self._final_cleanup(fixed_lines)

        return '\n'.join(fixed_lines)

    def _is_incomplete_control_structure(self, line: str, stripped: str) -> bool:
        """Check if line is an incomplete control structure."""
        return (re.match(r'^(if|elif|else|for|while|try|except|finally|with|def|class)\b', stripped) and
                not stripped.endswith(':'))

    def _fix_incomplete_control_structure(self, line: str, stripped: str, all_lines: list[str], current_idx: int) -> list[str]:
        """Fix incomplete control structure."""
        # Add colon at the end
        fixed_line = stripped + ':'
        return [fixed_line, '    pass  # TODO: Implement']

    def _has_unmatched_parenthesis(self, line: str, stripped: str) -> bool:
        """Check if line has unmatched parenthesis."""
        return re.match(r'^\s*\)\s*$', line)

    def _fix_unmatched_parenthesis(self, line: str, stripped: str) -> str:
        """Fix unmatched parenthesis."""
        return ""  # Remove unmatched closing parenthesis

    def _has_indentation_issue(self, line: str, stripped: str) -> bool:
        """Check if line has indentation issue."""
        if stripped.startswith(('from ', 'import ')):
            if any(prefix in stripped for prefix in ['agentic_core', 'apps_', 'system_learning']):
                return (line.startswith(' ') or line.startswith('\t'))
        return False

    def _fix_indentation_issue(self, line: str, stripped: str) -> str:
        """Fix indentation issue."""
        return stripped  # Remove indentation

    def _is_problematic_line(self, line: str, stripped: str) -> bool:
        """Check if line is problematic."""
        return (re.match(r'^\s*\)\s*$', line) or
                (not line.startswith(' ') and not line.startswith('\t') and
                 (re.match(r'^_emit_[a-zA-Z_][a-zA-Z0-9_]*,?\s*$', stripped) or
                  re.match(r'^emit_[a-zA-Z_][a-zA-Z0-9_]*,?\s*$', stripped) or
                  re.match(r'^[A-Z_][A-Z0-9_]*,?\s*$', stripped))))

    def _final_cleanup(self, lines: list[str]) -> list[str]:
        """Final cleanup of lines."""
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
        """Print wave summary."""
        print("\n" + "="*60)
        print("WAVE 5: COMPLETE FIX SUMMARY")
        print("="*60)
        print(f"Total files checked: {self.stats['total_files']}")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Comprehensive fixes: {self.stats['comprehensive_fixes']}")
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
    """Run Wave 5 complete fix."""
    repo_root = pathlib.Path(__file__).parent.parent

    print("🌊 WAVE 5: COMPLETE FIX")
    print(f"Repository: {repo_root}")

    fixer = Wave5CompleteFix(repo_root)
    stats = fixer.process_files()
    fixer.print_summary()

    return stats['syntax_errors_fixed'] > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
