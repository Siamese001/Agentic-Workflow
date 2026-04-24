#!/usr/bin/env python3
"""Aggressive syntax fix - remove all migration artifacts completely."""

import ast
import pathlib
import re


class AggressiveSyntaxFixer:
    """Aggressive fixer that removes all migration artifacts."""

    def __init__(self, repo_root: pathlib.Path):
        self.repo_root = repo_root
        self.tests_dir = repo_root / "tests"
        self.stats = {
            "total_files": 0,
            "syntax_errors_fixed": 0,
            "all_migration_artifacts_removed": 0,
            "files_with_errors": 0,
        }
        self.failed_files: list[tuple[str, str]] = []

    def fix_active_test_files(self) -> dict:
        """Fix syntax errors using aggressive approach."""
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
            self.stats["total_files"] += 1
            if self.fix_file(test_file):
                self.stats["files_with_errors"] += 1

        return self.stats

    def fix_file(self, file_path: pathlib.Path) -> bool:
        """Fix syntax errors in a single file using aggressive approach."""
        try:
            original_content = file_path.read_text(encoding="utf-8")
        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            self.failed_files.append((str(file_path), f"Read error: {e}"))
            return False

        # Check if file has syntax errors
        try:
            ast.parse(original_content)
            return False  # No syntax errors, skip
        except SyntaxError:
            pass  # File has syntax errors, needs fixing

        # Apply aggressive fix
        fixed_content = self._aggressive_syntax_fix(original_content)

        # Validate the fix
        try:
            ast.parse(fixed_content)
            # If successful, write back
            file_path.write_text(fixed_content, encoding="utf-8")
            self.stats["syntax_errors_fixed"] += 1
            return True
        except SyntaxError as e:
            self.failed_files.append((str(file_path), f"Syntax error after fix: {e}"))
            return False

    def _aggressive_syntax_fix(self, content: str) -> str:
        """Apply aggressive fix to remove all migration artifacts."""
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

            # Remove ANY line that contains migration artifacts
            if "#  # MOVED:" in line or "#  # MOVED:" in stripped or stripped.startswith("#  # MOVED:"):
                # Remove this line and ALL subsequent indented lines
                self.stats["all_migration_artifacts_removed"] += 1
                i += 1

                # Skip all following indented lines
                while i < len(lines):
                    next_line = lines[i]
                    if next_line.strip() and not next_line.startswith(" ") and not next_line.startswith("\t"):
                        break
                    i += 1

                continue

            # Remove orphaned import content (lines that look like import content but aren't proper imports)
            if (
                not stripped.startswith("#")
                and not stripped.startswith(
                    (
                        "from ",
                        "import ",
                        "def ",
                        "class ",
                        "@",
                        '"""',
                        "'''",
                        "try:",
                        "except",
                        "finally:",
                        "if ",
                        "elif ",
                        "else:",
                        "for ",
                        "while ",
                        "with ",
                        "return ",
                        "yield ",
                        "raise ",
                        "break",
                        "continue",
                        "pass",
                        "global",
                        "nonlocal",
                    )
                )
                and (
                    any(
                        keyword in stripped
                        for keyword in [
                            "_emit_",
                            "MAX_",
                            "BATCH_",
                            "BUFFER_",
                            "DEFAULT_",
                            "MAX_",
                            "RETRIES_",
                            "THRESHOLD",
                        ]
                    )
                    or re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*,?\s*$", stripped)
                    or re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*\s*#.*$", stripped)
                )
            ):
                # This looks like orphaned import content, remove it
                i += 1
                continue

            # Remove unmatched closing parentheses
            if re.match(r"^\s*\)\s*$", line):
                i += 1
                continue

            # Keep everything else
            fixed_lines.append(line)
            i += 1

        # Clean up multiple consecutive empty lines
        cleaned_lines = []
        prev_empty = False
        for line in fixed_lines:
            if not line.strip():
                if not prev_empty:
                    cleaned_lines.append(line)
                prev_empty = True
            else:
                cleaned_lines.append(line)
                prev_empty = False

        return "\n".join(cleaned_lines)

    def print_summary(self):
        """Print fixing summary."""
        print("\n" + "=" * 60)
        print("AGGRESSIVE SYNTAX FIX SUMMARY")
        print("=" * 60)
        print(f"Total files checked: {self.stats['total_files']}")
        print(f"Files with errors fixed: {self.stats['files_with_errors']}")
        print(f"Syntax errors fixed: {self.stats['syntax_errors_fixed']}")
        print(f"Migration artifacts removed: {self.stats['all_migration_artifacts_removed']}")
        print(f"Failed files: {len(self.failed_files)}")

        if self.failed_files:
            print("\nFailed files (first 10):")
            for file_path, error in self.failed_files[:10]:
                print(f"  {file_path}: {error}")
            if len(self.failed_files) > 10:
                print(f"  ... and {len(self.failed_files) - 10} more")

        print("=" * 60)


def main():
    """Run aggressive syntax fix."""
    repo_root = pathlib.Path(__file__).parent.parent

    print("🔥 AGGRESSIVE SYNTAX FIX - COMPLETE MIGRATION ARTIFACT REMOVAL")
    print(f"Repository: {repo_root}")

    fixer = AggressiveSyntaxFixer(repo_root)
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
            content = test_file.read_text(encoding="utf-8")
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
