#!/usr/bin/env python3
"""Fixed import migrator - properly moves top-level app imports into test functions.

This version actually moves imports instead of commenting them out.
"""

import ast
import pathlib
import re
import sys

# Target import patterns to migrate
TARGET_IMPORT_RE = re.compile(
    r'^\s*(from\s+(agentic_core|apps_|system_learning|infrastructure)\S*\s+import\s+.*|import\s+(agentic_core|apps_|system_learning|infrastructure)\S+)',
    re.MULTILINE,
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

class FixedImportMigrator:
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
        """Migrate a single test file using proper AST manipulation."""
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

        # Analyze which imports are used where
        import_usage = self._analyze_import_usage(tree, top_imports)

        # Generate new content with moved imports
        new_content = self._generate_migrated_content(content, top_imports, import_usage)

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
                line = content.splitlines()[node.lineno - 1]
                return TARGET_IMPORT_RE.match(line) is not None
        return False

    def _analyze_import_usage(self, tree: ast.AST, imports: list[ast.AST]) -> dict[str, list[str]]:
        """Analyze which imported symbols are used in which test functions/fixtures."""
        usage = {}

        # Map imported names to their import statements
        import_map = {}
        for imp in imports:
            if isinstance(imp, ast.Import):
                for alias in imp.names:
                    import_map[alias.asname or alias.name] = imp
            elif isinstance(imp, ast.ImportFrom):
                for alias in imp.names:
                    import_map[alias.asname or alias.name] = imp

        # Find usage in each test function/fixture
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith('test_') or node.name.startswith('fixture_'):
                    used_imports = set()
                    for subnode in ast.walk(node):
                        if isinstance(subnode, ast.Name) and subnode.id in import_map:
                            used_imports.add(subnode.id)

                    if used_imports:
                        usage[node.name] = list(used_imports)

        return usage

    def _generate_migrated_content(self, content: str, imports: list[ast.AST],
                                 usage: dict[str, list[str]]) -> str:
        """Generate new content with imports moved into functions."""
        lines = content.splitlines()

        # Remove top-level target imports
        new_lines = []
        for i, line in enumerate(lines):
            should_remove = False
            for imp in imports:
                imp_line_num = imp.lineno - 1
                if i == imp_line_num:
                    should_remove = True
                    break
            if not should_remove:
                new_lines.append(line)

        # Add imports to functions that use them
        for func_name, used_names in usage.items():
            # Find the function definition
            func_start = None
            func_indent = None
            for i, line in enumerate(new_lines):
                if f"def {func_name}(" in line:
                    func_start = i
                    func_indent = len(line) - len(line.lstrip())
                    break

            if func_start is not None:
                # Insert imports after function definition
                import_lines = []
                for imp in imports:
                    if isinstance(imp, ast.Import):
                        for alias in imp.names:
                            if (alias.asname or alias.name) in used_names:
                                import_lines.append(f"{' ' * (func_indent + 4)}{ast.unparse(imp)}")
                                break
                    elif isinstance(imp, ast.ImportFrom):
                        for alias in imp.names:
                            if (alias.asname or alias.name) in used_names:
                                import_lines.append(f"{' ' * (func_indent + 4)}{ast.unparse(imp)}")
                                break

                if import_lines:
                    # Insert imports after function docstring or first line
                    insert_pos = func_start + 1
                    # Look for docstring
                    if insert_pos < len(new_lines):
                        for j in range(insert_pos, min(insert_pos + 3, len(new_lines))):
                            if new_lines[j].strip().endswith(('"""', "'''")):
                                insert_pos = j + 1
                                break

                    for import_line in reversed(import_lines):
                        new_lines.insert(insert_pos, import_line)

        return '\n'.join(new_lines) + '\n'

    def print_summary(self):
        """Print migration summary."""
        print("\n=== Migration Summary ===")
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
        print("Usage: python fixed_import_migrator.py <test_directory>")
        sys.exit(1)

    repo_root = pathlib.Path(__file__).parent.parent
    test_dir = sys.argv[1]

    migrator = FixedImportMigrator(repo_root)
    migrator.migrate_directory(test_dir)
    migrator.print_summary()

if __name__ == "__main__":
    main()
