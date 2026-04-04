#!/usr/bin/env python3
"""Wave 7: Block Completion - Fix incomplete code blocks.

This wave focuses on completing incomplete code blocks that are
causing "expected an indented block" errors.
"""

import ast
import pathlib
import re


class Wave7BlockCompletion:
    """Wave 7: Complete incomplete code blocks."""

    def __init__(self, repo_root: pathlib.Path):
        self.repo_root = repo_root
        self.tests_dir = repo_root / "tests"
        self.stats = {
            'total_files': 0,
            'files_processed': 0,
            'blocks_completed': 0,
            'syntax_errors_fixed': 0,
            'failed_files': 0
        }
        self.failed_files: list[tuple[str, str]] = []

    def process_files(self) -> dict:
        """Process files with Wave 7 block completion."""
        # Only process files in tests/ directory, exclude archives
        test_files = []
        for pattern in ["test_*.py", "*/test_*.py"]:
            test_files.extend(self.tests_dir.rglob(pattern))

        # Filter out archive directories and already valid files
        active_test_files = []
        for test_file in test_files:
            if "archive" not in str(test_file).lower():
                # Check if file has syntax errors
                try:
                    content = test_file.read_text(encoding='utf-8')
                    ast.parse(content)
                    continue  # Skip valid files
                except SyntaxError:
                    active_test_files.append(test_file)
                except UnicodeDecodeError:
                    continue

        print(f"Wave 7: Processing {len(active_test_files)} files with syntax errors...")

        for test_file in active_test_files:
            self.stats['total_files'] += 1
            if self.process_file(test_file):
                self.stats['files_processed'] += 1

        return self.stats

    def process_file(self, file_path: pathlib.Path) -> bool:
        """Process a single file with block completion."""
        try:
            original_content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.failed_files.append((str(file_path), f"Read error: {e}"))
            return False

        # Apply block completion
        fixed_content = self._complete_blocks(original_content)

        # Validate the fix
        try:
            ast.parse(fixed_content)
            file_path.write_text(fixed_content, encoding='utf-8')
            self.stats['syntax_errors_fixed'] += 1
            return True
        except SyntaxError as e:
            # Try minimal fix
            minimal_content = self._minimal_block_fix(original_content)
            try:
                ast.parse(minimal_content)
                file_path.write_text(minimal_content, encoding='utf-8')
                self.stats['syntax_errors_fixed'] += 1
                return True
            except SyntaxError as e2:
                self.failed_files.append((str(file_path), f"Block completion failed: {e2}"))
                return False

    def _complete_blocks(self, content: str) -> str:
        """Complete incomplete code blocks."""
        lines = content.splitlines()
        fixed_lines = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                fixed_lines.append(line)
                continue

            # Check for incomplete blocks
            if self._is_incomplete_block(line, stripped):
                completed_lines = self._complete_block(line, stripped, lines, i)
                fixed_lines.extend(completed_lines)
                self.stats['blocks_completed'] += 1
            else:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def _is_incomplete_block(self, line: str, stripped: str) -> bool:
        """Check if line starts an incomplete block."""
        return (re.match(r'^(def|class|if|elif|else|for|while|try|except|finally|with)\b', stripped) and
                not stripped.endswith(':'))

    def _complete_block(self, line: str, stripped: str, all_lines: list[str], current_idx: int) -> list[str]:
        """Complete an incomplete block."""
        # Add colon and pass statement
        completed_line = stripped + ':'

        # Determine appropriate content for the block
        if stripped.startswith('def '):
            return [completed_line, '    pass  # TODO: Implement function']
        elif stripped.startswith('class '):
            return [completed_line, '    pass  # TODO: Implement class']
        elif stripped.startswith(('if', 'elif', 'else', 'for', 'while', 'try', 'except', 'finally', 'with')):
            return [completed_line, '    pass  # TODO: Implement block']
        else:
            return [completed_line, '    pass  # TODO: Implement']

    def _minimal_block_fix(self, content: str) -> str:
        """Apply minimal block fix."""
        lines = content.splitlines()
        fixed_lines = []

        for line in lines:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                fixed_lines.append(line)
                continue

            # Fix incomplete blocks minimally
            if self._is_incomplete_block(line, stripped):
                fixed_lines.append(stripped + ':')
                fixed_lines.append('    pass')
            else:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def print_summary(self):
        """Print wave summary."""
        print("\n" + "="*60)
        print("WAVE 7: BLOCK COMPLETION SUMMARY")
        print("="*60)
        print(f"Total files checked: {self.stats['total_files']}")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Blocks completed: {self.stats['blocks_completed']}")
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
    """Run Wave 7 block completion."""
    repo_root = pathlib.Path(__file__).parent.parent

    print("🌊 WAVE 7: BLOCK COMPLETION")
    print(f"Repository: {repo_root}")

    completer = Wave7BlockCompletion(repo_root)
    stats = completer.process_files()
    completer.print_summary()

    return stats['syntax_errors_fixed'] > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
