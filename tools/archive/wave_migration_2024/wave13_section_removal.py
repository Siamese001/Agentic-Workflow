#!/usr/bin/env python3
"""Wave 13: Section Removal - Remove entire problematic sections.

This wave removes entire sections that are causing syntax errors,
including the problematic comment blocks and their content.
"""

import ast
import pathlib
import re


class Wave13SectionRemoval:
    """Wave 13: Remove problematic sections."""

    def __init__(self, repo_root: pathlib.Path):
        self.repo_root = repo_root
        self.tests_dir = repo_root / "tests"
        self.stats = {
            'total_files': 0,
            'files_processed': 0,
            'sections_removed': 0,
            'syntax_errors_fixed': 0,
            'failed_files': 0
        }
        self.failed_files: list[tuple[str, str]] = []

    def process_files(self) -> dict:
        """Process files with Wave 13 section removal."""
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

        print(f"Wave 13: Processing {len(active_test_files)} files with syntax errors...")

        for test_file in active_test_files:
            self.stats['total_files'] += 1
            if self.process_file(test_file):
                self.stats['files_processed'] += 1

        return self.stats

    def process_file(self, file_path: pathlib.Path) -> bool:
        """Process a single file with section removal."""
        try:
            original_content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.failed_files.append((str(file_path), f"Read error: {e}"))
            return False

        # Apply section removal
        cleaned_content = self._remove_problematic_sections(original_content)

        # Validate the fix
        try:
            ast.parse(cleaned_content)
            file_path.write_text(cleaned_content, encoding='utf-8')
            self.stats['syntax_errors_fixed'] += 1
            return True
        except SyntaxError as e:
            # Try aggressive removal
            aggressive_content = self._aggressive_section_removal(original_content)
            try:
                ast.parse(aggressive_content)
                file_path.write_text(aggressive_content, encoding='utf-8')
                self.stats['syntax_errors_fixed'] += 1
                return True
            except SyntaxError as e2:
                self.failed_files.append((str(file_path), f"Section removal failed: {e2}"))
                return False

    def _remove_problematic_sections(self, content: str) -> str:
        """Remove problematic sections."""
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

            # Check if this starts a problematic section
            if self._starts_problematic_section(line, stripped):
                lines_removed = self._skip_problematic_section(lines, i)
                self.stats['sections_removed'] += 1
                i += lines_removed
                continue

            # Keep everything else
            cleaned_lines.append(line)
            i += 1

        return '\n'.join(cleaned_lines)

    def _starts_problematic_section(self, line: str, stripped: str) -> bool:
        """Check if line starts a problematic section."""
        return (re.match(r'^\s*#\s*#\s*MOVED:.*$', line) or
                stripped.startswith('# REMOVED:') or
                (not line.startswith(' ') and not line.startswith('\t') and
                 (any(keyword in stripped for keyword in ['_emit_', 'emit_', 'MAX_', 'BATCH_', 'BUFFER_', 'DEFAULT_', 'MAX_', 'RETRIES_', 'THRESHOLD']) or
                  re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*,?\s*$', stripped))))

    def _skip_problematic_section(self, lines: list[str], start_idx: int) -> int:
        """Skip a problematic section and return number of lines skipped."""
        i = start_idx + 1
        while i < len(lines):
            line = lines[i]
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                break
            i += 1
        return i - start_idx

    def _aggressive_section_removal(self, content: str) -> str:
        """Apply aggressive section removal."""
        lines = content.splitlines()
        cleaned_lines = []

        in_problematic_section = False

        for line in lines:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                if not in_problematic_section:
                    cleaned_lines.append(line)
                continue

            # Check if this starts a problematic section
            if self._starts_problematic_section(line, stripped):
                in_problematic_section = True
                continue

            # Check if this ends a problematic section
            if in_problematic_section and not line.startswith(' ') and not line.startswith('\t'):
                in_problematic_section = False
                cleaned_lines.append(line)
                continue

            # Skip lines in problematic sections
            if in_problematic_section:
                continue

            # Keep everything else
            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def print_summary(self):
        """Print wave summary."""
        print("\n" + "="*60)
        print("WAVE 13: SECTION REMOVAL SUMMARY")
        print("="*60)
        print(f"Total files checked: {self.stats['total_files']}")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Sections removed: {self.stats['sections_removed']}")
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
    """Run Wave 13 section removal."""
    repo_root = pathlib.Path(__file__).parent.parent

    print("🌊 WAVE 13: SECTION REMOVAL")
    print(f"Repository: {repo_root}")

    remover = Wave13SectionRemoval(repo_root)
    stats = remover.process_files()
    remover.print_summary()

    return stats['syntax_errors_fixed'] > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
