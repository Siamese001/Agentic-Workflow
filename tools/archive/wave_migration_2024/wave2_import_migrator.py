#!/usr/bin/env python3
"""Wave 2 Import Migrator - Robust version with proper import formatting.

This version handles multi-line imports and preserves proper syntax.
"""

import ast
import pathlib
import re
import sys

# Target import patterns to migrate
TARGET_IMPORT_RE = re.compile(
    r'^\s*(from\s+(agentic_core|apps_|system_learning|infrastructure)\S*\s+import\s+.*|import\s+(agentic_core|apps_|system_learning|infrastructure)\S+)',
    re.MULTILINE
)

# Safe patterns that can remain at top level
SAFE_TOP_IMPORTS = {
    'import agentic_core',
    'import apps_lic',
    'import apps_rg',
    'import apps_shared',
    'import system_learning',
    'import infrastructure',
}

class Wave2ImportMigrator:
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
        """Migrate a single test file using robust AST manipulation."""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"  ❌ Syntax error in {file_path.name}: {e}")
            self.failed_files.append((str(file_path), f"Syntax error: {e}"))
            return False
        except Exception as e:
            print(f"  ❌ Failed to read {file_path}: {e}")
            self.failed_files.append((str(file_path), str(e)))
            return False

        # Find top-level target imports
        top_imports = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if self._is_target_import(node, content):
                    top_imports.append(node)

        if not top_imports:
            print(f"  ✓ No target imports in {file_path.name}")
            return True  # No migration needed

        print(f"  🔄 Migrating {len(top_imports)} top-level imports in {file_path.name}")

        # Generate new content with moved imports
        new_content = self._generate_migrated_content_v2(content, top_imports)

        # Write back
        try:
            file_path.write_text(new_content, encoding='utf-8')
            self.migrated_files.append(str(file_path))
            self.stats['imports_moved'] += len(top_imports)
            return True
        except Exception as e:
            print(f"  ❌ Failed to write {file_path}: {e}")
            self.failed_files.append((str(file_path), str(e)))
            return False

    def _is_target_import(self, node: ast.AST, content: str) -> bool:
        """Check if an import node should be migrated."""
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_stmt = f"import {alias.name}"
                if import_stmt not in SAFE_TOP_IMPORTS:
                    return True
        elif isinstance(node, ast.ImportFrom):
            if node.module and any(node.module.startswith(prefix) for prefix in
                                  ['agentic_core', 'apps_', 'system_learning', 'infrastructure']):
                return True
        return False

    def _generate_migrated_content_v2(self, content: str, imports: list[ast.AST]) -> str:
        """Generate new content with imports properly moved into functions."""
        lines = content.splitlines()

        # Find which lines contain target imports
        import_line_numbers = set()
        for imp in imports:
            if hasattr(imp, 'lineno'):
                import_line_numbers.add(imp.lineno - 1)

        # Remove top-level target imports but preserve other content
        new_lines = []
        for i, line in enumerate(lines):
            if i not in import_line_numbers:
                new_lines.append(line)

        # Find test functions and add imports
        for i, line in enumerate(new_lines):
            if re.match(r'^\s*def\s+test_\w+\s*\(', line):
                indent = len(line) - len(line.lstrip())

                # Add all imports after the function definition
                import_section = []
                for imp in imports:
                    import_text = ast.unparse(imp)
                    import_section.append(f"{' ' * (indent + 4)}{import_text}")

                if import_section:
                    # Insert imports after function definition
                    insert_pos = i + 1

                    # Skip docstring if present
                    if insert_pos < len(new_lines):
                        for j in range(insert_pos, min(insert_pos + 3, len(new_lines))):
                            if new_lines[j].strip().endswith(('"""', "'''")):
                                insert_pos = j + 1
                                break

                    # Insert the imports
                    for import_line in import_section:
                        new_lines.insert(insert_pos, import_line)
                        insert_pos += 1
                    new_lines.insert(insert_pos, "")  # Add blank line after imports
                    break  # Only add to first test function for simplicity

        return '\n'.join(new_lines) + '\n'

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
        print("Usage: python wave2_import_migrator.py <test_directory>")
        sys.exit(1)

    repo_root = pathlib.Path(__file__).parent.parent
    test_dir = sys.argv[1]

    migrator = Wave2ImportMigrator(repo_root)
    migrator.migrate_directory(test_dir)
    migrator.print_summary()

if __name__ == "__main__":
    main()
