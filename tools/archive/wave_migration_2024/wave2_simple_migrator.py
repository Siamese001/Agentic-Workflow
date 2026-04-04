#!/usr/bin/env python3
"""Wave 2 Simple Import Migrator - Text-based approach for reliability.

Uses regex and text manipulation to avoid AST parsing issues.
"""

import pathlib
import re
import sys

# Target import patterns to migrate
TARGET_IMPORT_RE = re.compile(
    r'^\s*(from\s+(agentic_core|apps_|system_learning|infrastructure)\S*\s+import\s+.*|import\s+(agentic_core|apps_|system_learning|infrastructure)\S+)',
    re.MULTILINE
)

# Function start pattern
FUNC_START_RE = re.compile(r'^(\s*)def\s+(test_\w+)\s*\(', re.MULTILINE)

class Wave2SimpleMigrator:
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
        """Migrate a single test file using text-based approach."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"  ❌ Failed to read {file_path}: {e}")
            self.failed_files.append((str(file_path), str(e)))
            return False

        # Find top-level target imports
        import_lines = []
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if TARGET_IMPORT_RE.match(line):
                import_lines.append((i, line))

        if not import_lines:
            print(f"  ✓ No target imports in {file_path.name}")
            return True  # No migration needed

        print(f"  🔄 Migrating {len(import_lines)} top-level imports in {file_path.name}")

        # Find first test function
        first_func_match = None
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
        moved_imports = []

        # Remove imports and collect them
        for i, line in enumerate(lines):
            is_import_line = any(i == import_idx for import_idx, _ in import_lines)
            if is_import_line:
                moved_imports.append(line)
            else:
                new_lines.append(line)

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
                indented_import = ' ' * (func_indent + 4) + import_line.strip()
                new_lines.insert(insert_pos, indented_import)
                insert_pos += 1

            # Add blank line after imports
            new_lines.insert(insert_pos, '')

        new_content = '\n'.join(new_lines) + '\n'

        # Write back
        try:
            file_path.write_text(new_content, encoding='utf-8')
            self.migrated_files.append(str(file_path))
            self.stats['imports_moved'] += len(import_lines)
            return True
        except Exception as e:
            print(f"  ❌ Failed to write {file_path}: {e}")
            self.failed_files.append((str(file_path), str(e)))
            return False

    def print_summary(self):
        """Print migration summary."""
        print("\n=== Wave 2 Migration Summary ===")
        print(f"Total files processed: {self.stats['total_files']}")
        print(f"Successfully migrated: {self.stats['migrated']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Imports moved: {self.stats['imports_moved']}")

        if self.failed_files:
            print("\nFailed files:")
            for path, error in self.failed_files[:10]:
                print(f"  {path}: {error}")
            if len(self.failed_files) > 10:
                print(f"  ... and {len(self.failed_files) - 10} more")

def main():
    if len(sys.argv) != 2:
        print("Usage: python wave2_simple_migrator.py <test_directory>")
        sys.exit(1)

    repo_root = pathlib.Path(__file__).parent.parent
    test_dir = sys.argv[1]

    migrator = Wave2SimpleMigrator(repo_root)
    migrator.migrate_directory(test_dir)
    migrator.print_summary()

if __name__ == "__main__":
    main()
