#!/usr/bin/env python3
"""Advanced syntax fix for complex migration issues.

This script handles the specific pattern where imports were moved
but left at module level without proper indentation.
"""

import ast
import pathlib
import re


class AdvancedSyntaxFixer:
    """Advanced fixer for complex syntax errors in migrated test files."""

    def __init__(self, repo_root: pathlib.Path):
        self.repo_root = repo_root
        self.tests_dir = repo_root / "tests"
        self.stats = {
            'total_files': 0,
            'syntax_errors_fixed': 0,
            'legacy_comments_removed': 0,
            'imports_moved_to_functions': 0,
            'unmatched_parens_removed': 0,
            'files_with_errors': 0
        }
        self.failed_files: list[tuple[str, str]] = []

    def fix_active_test_files(self) -> dict:
        """Fix syntax errors in active test files using advanced techniques."""
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
        """Fix syntax errors in a single file using advanced techniques."""
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

        # Apply advanced fix
        fixed_content = self._advanced_syntax_fix(original_content)

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

    def _advanced_syntax_fix(self, content: str) -> str:
        """Apply advanced syntax fixes for complex migration issues."""
        lines = content.splitlines()
        fixed_lines = []

        # Track imports that need to be moved
        orphaned_imports = []

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                fixed_lines.append(line)
                i += 1
                continue

            # Remove legacy comment lines
            if re.match(r'^\s*#\s*#\s*MOVED:.*$', line):
                self.stats['legacy_comments_removed'] += 1
                i += 1
                continue

            # Remove lines that are just closing parentheses
            if re.match(r'^\s*\)\s*$', line):
                self.stats['unmatched_parens_removed'] += 1
                i += 1
                continue

            # Check for orphaned import lines (imports at module level that should be in functions)
            if (stripped.startswith(('from ', 'import ')) and
                any(prefix in stripped for prefix in ['agentic_core', 'apps_', 'system_learning'])):

                # If this import is at module level (no indentation), collect it
                if not line.startswith(' ') and not line.startswith('\t'):
                    orphaned_imports.append(stripped)
                    i += 1
                    continue
                else:
                    # This import is properly indented, keep it
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

            i += 1

        # Now, if we have orphaned imports, we need to move them to the first test function
        if orphaned_imports:
            fixed_lines = self._move_imports_to_first_test_function(fixed_lines, orphaned_imports)

        return '\n'.join(fixed_lines)

    def _move_imports_to_first_test_function(self, lines: list[str], imports: list[str]) -> list[str]:
        """Move orphaned imports to the first test function."""
        result_lines = []
        imports_moved = False

        for i, line in enumerate(lines):
            # Check if this is the start of a test function
            if re.match(r'^\s*def\s+test_\w+', line):
                # Add the imports before this function
                if not imports_moved:
                    # Add imports with proper indentation
                    indent_match = re.match(r'^(\s*)def\s+test_\w+', line)
                    if indent_match:
                        base_indent = indent_match.group(1)
                        import_indent = base_indent + '    '

                        for import_line in imports:
                            result_lines.append(f"{import_indent}{import_line}")

                        # Add blank line after imports
                        result_lines.append("")
                        imports_moved = True
                        self.stats['imports_moved_to_functions'] += 1

            result_lines.append(line)

        # If we didn't find any test functions, just append imports at the end
        if not imports_moved and imports:
            result_lines.extend([""] + imports)

        return result_lines

    def print_summary(self):
        """Print fixing summary."""
        print("\n" + "="*60)
        print("ADVANCED SYNTAX FIX SUMMARY")
        print("="*60)
        print(f"Total files checked: {self.stats['total_files']}")
        print(f"Files with errors fixed: {self.stats['files_with_errors']}")
        print(f"Syntax errors fixed: {self.stats['syntax_errors_fixed']}")
        print(f"Legacy comments removed: {self.stats['legacy_comments_removed']}")
        print(f"Imports moved to functions: {self.stats['imports_moved_to_functions']}")
        print(f"Unmatched parentheses removed: {self.stats['unmatched_parens_removed']}")
        print(f"Failed files: {len(self.failed_files)}")

        if self.failed_files:
            print("\nFailed files (first 10):")
            for file_path, error in self.failed_files[:10]:
                print(f"  {file_path}: {error}")
            if len(self.failed_files) > 10:
                print(f"  ... and {len(self.failed_files) - 10} more")

        print("="*60)


def main():
    """Run advanced syntax fix."""
    repo_root = pathlib.Path(__file__).parent.parent

    print("🔧 ADVANCED SYNTAX FIX - COMPLEX MIGRATION ISSUES")
    print(f"Repository: {repo_root}")

    fixer = AdvancedSyntaxFixer(repo_root)
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
        print("✅ ALL ACTIVE SYNTAX ERRORS FIXED!")
    else:
        print(f"⚠️  {syntax_errors} active files still have syntax errors")

    return syntax_errors == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
