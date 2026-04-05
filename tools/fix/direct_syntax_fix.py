#!/usr/bin/env python3
"""Direct syntax fix - remove all problematic sections completely.

This script takes a direct approach: if a file has syntax errors,
remove all migration artifacts and restore basic functionality.
"""

import ast
import pathlib
import re


class DirectSyntaxFixer:
    """Direct fixer that removes all problematic migration artifacts."""

    def __init__(self, repo_root: pathlib.Path):
        self.repo_root = repo_root
        self.tests_dir = repo_root / "tests"
        self.stats = {
            'total_files': 0,
            'syntax_errors_fixed': 0,
            'files_completely_cleaned': 0,
            'migration_artifacts_removed': 0,
            'files_with_errors': 0
        }
        self.failed_files: list[tuple[str, str]] = []

    def fix_active_test_files(self) -> dict:
        """Fix syntax errors using direct approach."""
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
            self.stats['total_files'] += 1
            if self.fix_file(test_file):
                self.stats['files_with_errors'] += 1

        return self.stats

    def fix_file(self, file_path: pathlib.Path) -> bool:
        """Fix syntax errors in a single file using direct approach."""
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

        # Apply direct fix
        fixed_content = self._direct_syntax_fix(original_content)

        # Validate the fix
        try:
            ast.parse(fixed_content)
            # If successful, write back
            file_path.write_text(fixed_content, encoding='utf-8')
            self.stats['syntax_errors_fixed'] += 1
            return True
        except SyntaxError as e:
            self.failed_files.append((str(file_path), f"Syntax error after fix: {e}"))
            return False

    def _direct_syntax_fix(self, content: str) -> str:
        """Apply direct fix to remove all migration artifacts."""
        lines = content.splitlines()
        cleaned_lines = []

        # Track if we're in a problematic section
        in_problem_section = False

        for line in lines:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                if not in_problem_section:
                    cleaned_lines.append(line)
                continue

            # Check if this line starts a problematic section
            if (self._is_legacy_comment(line) or
                self._is_removed_comment(line) or
                self._is_orphaned_import_start(line)):

                in_problem_section = True
                self.stats['migration_artifacts_removed'] += 1
                continue

            # Check if this line ends a problematic section
            if in_problem_section and not line.startswith(' ') and not line.startswith('\t'):
                in_problem_section = False
                # This line starts a new section, keep it
                cleaned_lines.append(line)
                continue

            # Skip lines in problematic sections
            if in_problem_section:
                continue

            # Remove standalone problematic lines
            if (self._is_orphaned_import_content(line, stripped) or
                self._is_unmatched_parenthesis(line)):
                continue

            # Keep everything else
            cleaned_lines.append(line)

        # Clean up the result
        cleaned_lines = self._final_cleanup(cleaned_lines)

        return '\n'.join(cleaned_lines)

    def _is_legacy_comment(self, line: str) -> bool:
        """Check if line is a legacy migration comment."""
        return ('#  # MOVED:' in line or
                line.strip().startswith('#  # MOVED:') or
                re.match(r'^\s*#\s*#\s*MOVED:.*$', line))

    def _is_removed_comment(self, line: str) -> bool:
        """Check if line is a removed migration comment."""
        return line.strip().startswith('# REMOVED:')

    def _is_orphaned_import_start(self, line: str) -> bool:
        """Check if line starts orphaned import content."""
        stripped = line.strip()
        return (not line.startswith(' ') and not line.startswith('\t') and
                (any(keyword in stripped for keyword in ['_emit_', 'emit_', 'MAX_', 'BATCH_', 'BUFFER_', 'DEFAULT_', 'MAX_', 'RETRIES_', 'THRESHOLD']) or
                 re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*,?\s*$', stripped)))

    def _is_orphaned_import_content(self, line: str, stripped: str) -> bool:
        """Check if line is orphaned import content."""
        if stripped.startswith('#') or stripped.startswith(('from ', 'import ', 'def ', 'class ', '@', '"""', "'''", 'try:', 'except', 'finally:', 'if ', 'elif ', 'else:', 'for ', 'while ', 'with ', 'return ', 'yield ', 'raise ', 'break', 'continue', 'pass', 'global', 'nonlocal')):
            return False

        # Check for orphaned patterns
        orphaned_patterns = [
            r'^_emit_[a-zA-Z_][a-zA-Z0-9_]*,?\s*#.*$',
            r'^_emit_[a-zA-Z_][a-zA-Z0-9_]*,?\s*$',
            r'^emit_[a-zA-Z_][a-zA-Z0-9_]*,?\s*#.*$',
            r'^emit_[a-zA-Z_][a-zA-Z0-9_]*,?\s*$',
            r'^[A-Z_][A-Z0-9_]*,?\s*#.*$',
            r'^[A-Z_][A-Z0-9_]*,?\s*$',
        ]

        for pattern in orphaned_patterns:
            if re.match(pattern, stripped):
                return True

        return False

    def _is_unmatched_parenthesis(self, line: str) -> bool:
        """Check if line is unmatched parenthesis."""
        return re.match(r'^\s*\)\s*$', line)

    def _final_cleanup(self, lines: list[str]) -> list[str]:
        """Perform final cleanup of the lines."""
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
        print("\n" + "="*60)
        print("DIRECT SYNTAX FIX SUMMARY")
        print("="*60)
        print(f"Total files checked: {self.stats['total_files']}")
        print(f"Files with errors fixed: {self.stats['files_with_errors']}")
        print(f"Syntax errors fixed: {self.stats['syntax_errors_fixed']}")
        print(f"Files completely cleaned: {self.stats['files_completely_cleaned']}")
        print(f"Migration artifacts removed: {self.stats['migration_artifacts_removed']}")
        print(f"Failed files: {len(self.failed_files)}")

        if self.failed_files:
            print("\nFailed files (first 10):")
            for file_path, error in self.failed_files[:10]:
                print(f"  {file_path}: {error}")
            if len(self.failed_files) > 10:
                print(f"  ... and {len(self.failed_files) - 10} more")

        print("="*60)


def main():
    """Run direct syntax fix."""
    repo_root = pathlib.Path(__file__).parent.parent

    print("⚡ DIRECT SYNTAX FIX - COMPLETE ARTIFACT REMOVAL")
    print(f"Repository: {repo_root}")

    fixer = DirectSyntaxFixer(repo_root)
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
            content = test_file.read_text(encoding='utf-8')
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
