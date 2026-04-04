#!/usr/bin/env python3
"""Wave 2 Final Import Migrator - Handles multi-line imports correctly.

This version preserves complete import statements including multi-line ones.
"""

import pathlib
import re
import sys

# Target import patterns to migrate (start of import)
TARGET_IMPORT_START_RE = re.compile(
    r'^\s*(from\s+(agentic_core|apps_|system_learning|infrastructure)\S*\s+import\s+.*|import\s+(agentic_core|apps_|system_learning|infrastructure)\S+)',
    re.MULTILINE
)

# Function start pattern
FUNC_START_RE = re.compile(r'^(\s*)def\s+(test_\w+)\s*\(', re.MULTILINE)

class Wave2FinalMigrator:
    def __init__(self, repo_root: pathlib.Path):
        self.repo_root = repo_root
        self.migrated_files = []
        self.failed_files = []
        self.stats = {
            'total_files': 0,
            'migrated': 0,
            'failed': 0,
            'imports_moved': 0,
        }

    def migrate_directory(self, test_dir: str) -> dict:
        """Migrate all test files in a directory."""
        test_path = self.repo_root / test_dir
        if not test_path.exists():
            print(f"Directory {test_dir} does not exist, skipping")
            return self.stats

        test_files = list(test_path.rglob("test_*.py"))
        print(f"Found {len(test_files)} test files in {test_dir}")

        for test_file in test_files:
            self.stats['total_files'] += 1
            if self.migrate_file(test_file):
                self.stats['migrated'] += 1
            else:
                self.stats['failed'] += 1

        return self.stats

    def migrate_file(self, file_path: pathlib.Path) -> bool:
        """Migrate a single test file using improved text-based approach."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"  ❌ Failed to read {file_path}: {e}")
            self.failed_files.append((str(file_path), str(e)))
            return False

        # Find complete import blocks (including multi-line)
        import_blocks = self._find_import_blocks(content)

        if not import_blocks:
            print(f"  ✓ No target imports in {file_path.name}")
            return True  # No migration needed

        print(f"  🔄 Migrating {len(import_blocks)} import blocks in {file_path.name}")

        # Find first test function
        first_func_match = None
        lines = content.splitlines()
        for line in lines:
            match = FUNC_START_RE.match(line)
            if match:
                first_func_match = match
                break

        if not first_func_match:
            print(f"  ⚠️  No test functions found in {file_path.name}")
            return False

        # Build new content
        new_lines = []

        # Remove import blocks and collect them
        removed_lines = set()
        for start_line, end_line, import_lines in import_blocks:
            for i in range(start_line, end_line + 1):
                removed_lines.add(i)

        # Also remove any lines that are just closing parentheses after imports
        for i, line in enumerate(lines):
            if i not in removed_lines and line.strip() == ')' and i > 0:
                # Check if previous line was removed (was part of import)
                if i - 1 in removed_lines:
                    removed_lines.add(i)

        moved_imports = []
        for i, line in enumerate(lines):
            if i not in removed_lines:
                new_lines.append(line)

        # Collect the complete import blocks
        for start_line, end_line, import_lines in import_blocks:
            moved_imports.extend(import_lines)

        # Insert imports after first test function
        func_indent = len(first_func_match.group(1))
        insert_pos = None
        for i, line in enumerate(new_lines):
            if line.strip().startswith(f"def {first_func_match.group(2)}("):
                insert_pos = i + 1
                break

        if insert_pos is not None:
            # Skip docstring if present
            if insert_pos < len(new_lines):
                for j in range(insert_pos, min(insert_pos + 3, len(new_lines))):
                    if new_lines[j].strip().endswith(('"""', "'''")):
                        insert_pos = j + 1
                        break

            # Insert imports with proper indentation
            for import_line in moved_imports:
                if import_line.strip():  # Skip empty lines
                    indented_import = ' ' * (func_indent + 4) + import_line.rstrip()
                    new_lines.insert(insert_pos, indented_import)
                    insert_pos += 1

            # Add blank line after imports
            new_lines.insert(insert_pos, '')

        new_content = '\n'.join(new_lines) + '\n'

        # Write back
        try:
            file_path.write_text(new_content, encoding='utf-8')
            self.migrated_files.append(str(file_path))
            self.stats['imports_moved'] += len(import_blocks)
            return True
        except Exception as e:
            print(f"  ❌ Failed to write {file_path}: {e}")
            self.failed_files.append((str(file_path), str(e)))
            return False

    def _find_import_blocks(self, content: str) -> list[tuple]:
        """Find complete import blocks including multi-line ones."""
        lines = content.splitlines()
        import_blocks = []

        i = 0
        while i < len(lines):
            line = lines[i]
            if TARGET_IMPORT_START_RE.match(line):
                # Found start of import
                start_line = i
                import_lines = [line]
                i += 1

                # Continue until we find the end of the import block
                while i < len(lines):
                    current_line = lines[i]
                    import_lines.append(current_line)

                    # Check if this line ends the import (has closing parenthesis or no continuation)
                    if ')' in current_line or not current_line.strip().endswith(','):
                        # Check if next line is not indented (end of multi-line import)
                        if i + 1 >= len(lines) or not lines[i + 1].startswith(' ' * 4):
                            break
                    i += 1

                end_line = i - 1
                import_blocks.append((start_line, end_line, import_lines))
            else:
                i += 1

        return import_blocks

    def print_summary(self):
        """Print migration summary."""
        print("\n=== Wave 2 Migration Summary ===")
        print(f"Total files processed: {self.stats['total_files']}")
        print(f"Successfully migrated: {self.stats['migrated']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Import blocks moved: {self.stats['imports_moved']}")

        if self.failed_files:
            print("\nFailed files:")
            for path, error in self.failed_files[:10]:
                print(f"  {path}: {error}")
            if len(self.failed_files) > 10:
                print(f"  ... and {len(self.failed_files) - 10} more")

def main():
    if len(sys.argv) != 2:
        print("Usage: python wave2_final_migrator.py <test_directory>")
        sys.exit(1)

    repo_root = pathlib.Path(__file__).parent.parent
    test_dir = sys.argv[1]

    migrator = Wave2FinalMigrator(repo_root)
    migrator.migrate_directory(test_dir)
    migrator.print_summary()

if __name__ == "__main__":
    main()
