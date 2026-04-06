"""
Fix Invalid Stubs - Auto-fix script for test stubs that only return success.

This script scans test files for invalid stubs (stubs that only return success
without error simulation) and applies automated fixes to add error simulation paths.

Usage:
    python tools/fix/fix_invalid_stubs.py [--dry-run] [--apply]

Options:
    --dry-run: Show what would be fixed without making changes
    --apply: Apply the fixes to files
"""
import argparse
import ast
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from agentic_core.L5_safety.validators.invalid_stub_validator import InvalidStubDetector


class InvalidStubFixer:
    """Fixer for invalid stub patterns in test files."""

    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = project_root
        self.dry_run = dry_run
        self.detector = InvalidStubDetector()
        self.fixed_count = 0
        self.skipped_count = 0
        self.error_count = 0

    def fix_file(self, file_path: Path) -> bool:
        """Fix invalid stubs in a single file."""
        print(f"\nScanning: {file_path.relative_to(self.project_root)}")

        # Scan file for violations
        result = self.detector.scan_file(file_path)

        if not result.violations:
            print("  ✓ No invalid stubs found")
            self.skipped_count += 1
            return False

        print(f"  Found {len(result.violations)} invalid stub(s)")

        # Read file content
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines(keepends=True)
        except Exception as e:
            print(f"  ✗ Error reading file: {e}")
            self.error_count += 1
            return False

        # Apply fixes for each violation
        modified = False
        for violation in result.violations:
            if self._fix_violation(file_path, lines, violation):
                modified = True

        if modified:
            if self.dry_run:
                print("  [DRY RUN] Would apply changes")
                self.fixed_count += 1
            else:
                # Write back the modified content
                try:
                    new_content = "".join(lines)
                    # Verify syntax
                    ast.parse(new_content)
                    file_path.write_text(new_content, encoding="utf-8")
                    print("  ✓ Applied fixes")
                    self.fixed_count += 1
                except SyntaxError as e:
                    print(f"  ✗ Syntax error after fix: {e}")
                    self.error_count += 1
                    return False
                except Exception as e:
                    print(f"  ✗ Error writing file: {e}")
                    self.error_count += 1
                    return False

        return modified

    def _fix_violation(self, file_path: Path, lines: list[str], violation) -> bool:
        """Fix a single violation by adding error simulation."""
        line_number = violation.line_number
        function_name = violation.metadata.get("function_name", "unknown")

        print(f"  Fixing: {function_name} (line {line_number})")

        # Find the function definition
        func_line_idx = line_number - 1
        if func_line_idx >= len(lines):
            print(f"    ✗ Line {line_number} out of range")
            return False

        func_line = lines[func_line_idx]

        # Check if already whitelisted (check previous line, matching validator logic)
        if func_line_idx > 0:
            prev_line = lines[func_line_idx - 1]
            if "# guardian: allow-invalid-stub" in prev_line:
                print(f"    ⊘ Already whitelisted")
                return False

        # Find the function body (indentation level)
        func_indent = len(func_line) - len(func_line.lstrip())
        body_indent = func_indent + 4

        # Find the return statement(s)
        return_indices = []
        for i in range(func_line_idx + 1, len(lines)):
            line = lines[i]
            if line.strip() and not line.strip().startswith("#"):
                # Check if we've exited the function
                if line.strip() and len(line) - len(line.lstrip()) <= func_indent:
                    break
                if "return" in line and "def " not in line:
                    return_indices.append(i)

        if not return_indices:
            print(f"    ⊘ No return statements found")
            return False

        # Insert error simulation before the first return
        first_return_idx = return_indices[0]
        indent = " " * body_indent

        # Generate fix based on function signature
        fix_lines = self._generate_fix_lines(function_name, indent)

        # Insert the fix before the first return
        lines.insert(first_return_idx, fix_lines)

        print(f"    ✓ Added error simulation")
        return True

    def _generate_fix_lines(self, function_name: str, indent: str) -> str:
        """Generate fix lines for adding error simulation."""
        # Generate a conditional with error return
        lines = [
            f"{indent}# Add error simulation\n",
            f"{indent}if error_condition:\n",
            f'{indent}    return {{"status": 404, "error": "Not found"}}\n',
        ]
        return "".join(lines)

    def scan_directory(self, directory: Path) -> None:
        """Scan all test files in a directory."""
        print(f"\nScanning directory: {directory.relative_to(self.project_root)}")

        # Find all test files
        test_files = []
        for pattern in ["test_*.py", "*_test.py"]:
            test_files.extend(directory.rglob(pattern))

        # Also scan files in tests/ directories
        for tests_dir in directory.rglob("tests"):
            if tests_dir.is_dir():
                test_files.extend(tests_dir.glob("*.py"))

        # Deduplicate
        test_files = sorted(set(test_files))

        print(f"Found {len(test_files)} test file(s)")

        for file_path in test_files:
            if file_path.is_file():
                try:
                    self.fix_file(file_path)
                except Exception as e:
                    print(f"  ✗ Error processing {file_path}: {e}")
                    self.error_count += 1

    def print_summary(self) -> None:
        """Print summary of fixes."""
        print("\n" + "=" * 60)
        print("Fix Summary")
        print("=" * 60)
        print(f"Files fixed: {self.fixed_count}")
        print(f"Files skipped: {self.skipped_count}")
        print(f"Errors: {self.error_count}")
        print("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Fix invalid stubs in test files")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without making changes",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the fixes to files",
    )
    parser.add_argument(
        "--directory",
        type=str,
        default=None,
        help="Specific directory to scan (default: scan all test files)",
    )

    args = parser.parse_args()

    # Default to dry-run unless --apply is specified
    dry_run = not args.apply

    if dry_run and not args.apply:
        print("Running in DRY-RUN mode (use --apply to make changes)")
    elif args.apply:
        print("Running in APPLY mode (changes will be made)")

    fixer = InvalidStubFixer(ROOT_DIR, dry_run=dry_run)

    if args.directory:
        target_dir = ROOT_DIR / args.directory
        if not target_dir.exists():
            print(f"Error: Directory not found: {target_dir}")
            sys.exit(1)
        fixer.scan_directory(target_dir)
    else:
        # Scan all test files in the project
        for tests_dir in [ROOT_DIR / "tests", ROOT_DIR / "agentic_core"]:
            if tests_dir.exists():
                fixer.scan_directory(tests_dir)

    fixer.print_summary()

    if fixer.error_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
