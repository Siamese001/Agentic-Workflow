#!/usr/bin/env python3
"""Wave 3: Block Removal - Remove entire problematic blocks.

This wave removes entire blocks of migration artifacts that are
causing persistent syntax errors.
"""

import ast
import pathlib
import re


class Wave3BlockRemoval:
    """Wave 3: Remove problematic blocks."""

    def __init__(self, repo_root: pathlib.Path):
        self.repo_root = repo_root
        self.tests_dir = repo_root / "tests"
        self.stats = {
            'total_files': 0,
            'files_processed': 0,
            'blocks_removed': 0,
            'lines_removed': 0,
            'syntax_errors_fixed': 0,
            'failed_files': 0
        }
        self.failed_files: list[tuple[str, str]] = []

    def process_files(self) -> dict:
        """Process files with Wave 3 block removal."""
        # Only process files in tests/ directory, exclude archives
        test_files = []
        for pattern in ["test_*.py", "*/test_*.py"]:
            test_files.extend(self.tests_dir.rglob(pattern))

        # Filter out archive directories
        active_test_files = []
        for test_file in test_files:
            if "archive" not in str(test_file).lower():
                active_test_files.append(test_file)

        print(f"Wave 3: Processing {len(active_test_files)} active test files...")

        for test_file in active_test_files:
            self.stats['total_files'] += 1
            if self.process_file(test_file):
                self.stats['files_processed'] += 1

        return self.stats

    def process_file(self, file_path: pathlib.Path) -> bool:
        """Process a single file with block removal."""
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

        # Apply block removal
        fixed_content = self._remove_problematic_blocks(original_content)

        # Validate the fix
        try:
            ast.parse(fixed_content)
            file_path.write_text(fixed_content, encoding='utf-8')
            self.stats['syntax_errors_fixed'] += 1
            return True
        except SyntaxError as e:
            self.failed_files.append((str(file_path), f"Syntax error after fix: {e}"))
            return False

    def _remove_problematic_blocks(self, content: str) -> str:
        """Remove problematic blocks of migration artifacts."""
        lines = content.splitlines()
        cleaned_lines = []

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                cleaned_lines.append(line)
                i += 1
                continue

            # Check if this starts a problematic block
            if self._starts_problematic_block(line, stripped):
                lines_removed = self._skip_problematic_block(lines, i)
                self.stats['blocks_removed'] += 1
                self.stats['lines_removed'] += lines_removed
                i += lines_removed
                continue

            # Remove standalone problematic lines
            if self._is_problematic_line(line, stripped):
                self.stats['lines_removed'] += 1
                i += 1
                continue

            # Keep everything else
            cleaned_lines.append(line)
            i += 1

        return '\n'.join(cleaned_lines)

    def _starts_problematic_block(self, line: str, stripped: str) -> bool:
        """Check if line starts a problematic block."""
        return (re.match(r'^\s*#\s*#\s*MOVED:.*$', line) or
                stripped.startswith('# REMOVED:') or
                (not line.startswith(' ') and not line.startswith('\t') and
                 (any(keyword in stripped for keyword in ['_emit_', 'emit_', 'MAX_', 'BATCH_', 'BUFFER_', 'DEFAULT_', 'MAX_', 'RETRIES_', 'THRESHOLD']) or
                  re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*,?\s*$', stripped))))

    def _skip_problematic_block(self, lines: list[str], start_idx: int) -> int:
        """Skip a problematic block and return number of lines skipped."""
        i = start_idx + 1
        while i < len(lines):
            line = lines[i]
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                break
            i += 1
        return i - start_idx

    def _is_problematic_line(self, line: str, stripped: str) -> bool:
        """Check if line is problematic."""
        return (re.match(r'^\s*\)\s*$', line) or
                (not line.startswith(' ') and not line.startswith('\t') and
                 (re.match(r'^_emit_[a-zA-Z_][a-zA-Z0-9_]*,?\s*$', stripped) or
                  re.match(r'^emit_[a-zA-Z_][a-zA-Z0-9_]*,?\s*$', stripped) or
                  re.match(r'^[A-Z_][A-Z0-9_]*,?\s*$', stripped))))

    def print_summary(self):
        """Print wave summary."""
        print("\n" + "="*60)
        print("WAVE 3: BLOCK REMOVAL SUMMARY")
        print("="*60)
        print(f"Total files checked: {self.stats['total_files']}")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Blocks removed: {self.stats['blocks_removed']}")
        print(f"Lines removed: {self.stats['lines_removed']}")
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
    """Run Wave 3 block removal."""
    repo_root = pathlib.Path(__file__).parent.parent

    print("🌊 WAVE 3: BLOCK REMOVAL")
    print(f"Repository: {repo_root}")

    remover = Wave3BlockRemoval(repo_root)
    stats = remover.process_files()
    remover.print_summary()

    return stats['syntax_errors_fixed'] > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
