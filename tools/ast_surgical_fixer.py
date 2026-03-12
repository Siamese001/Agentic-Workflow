#!/usr/bin/env python3
"""
AST-Based Surgical Threshold Fixer

Uses pure AST manipulation to fix threshold=0.95 violations.
NO REGEX. Only AST node transformations.
"""

import ast
import sys
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root


class ThresholdTransformer(ast.NodeTransformer):
    """Transform threshold=0.95 keyword args to use THRESHOLD constant."""

    def __init__(self):
        self.modified = False
        self.modifications = []

    def visit_keyword(self, node: ast.keyword) -> ast.keyword:
        """Replace threshold=0.95 in function calls."""
        if node.arg == 'threshold':
            if isinstance(node.value, ast.Constant):
                if node.value.value == 0.95:
                    # Replace with THRESHOLD reference
                    node.value = ast.Name(id='THRESHOLD', ctx=ast.Load())
                    self.modified = True
                    self.modifications.append({
                        'line': getattr(node, 'lineno', 0),
                        'type': 'keyword_arg',
                    })
        return node


class ImportAdder(ast.NodeTransformer):
    """Add THRESHOLD to existing path_constants import or create new import."""

    def __init__(self):
        self.has_path_constants_import = False
        self.has_threshold_import = False
        self.import_node_index = None
        self.added_import = False

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """Process module to add import if needed."""
        # First pass: check existing imports
        for i, stmt in enumerate(node.body):
            if isinstance(stmt, ast.ImportFrom):
                if stmt.module and 'path_constants' in stmt.module:
                    self.has_path_constants_import = True
                    self.import_node_index = i

                    # Check if THRESHOLD already imported
                    for alias in stmt.names:
                        if alias.name == 'THRESHOLD':
                            self.has_threshold_import = True
                            break

                    if not self.has_threshold_import:
                        # Add THRESHOLD to existing import
                        stmt.names.append(ast.alias(name='THRESHOLD', asname=None))
                        self.added_import = True
                    break

        # If no path_constants import found, add new import after other imports
        if not self.has_path_constants_import:
            # Find last import position
            last_import_idx = 0
            for i, stmt in enumerate(node.body):
                if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                    last_import_idx = i + 1
                elif not isinstance(stmt, ast.Expr):
                    # Stop at first non-import, non-docstring statement
                    if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant)):
                        break

            # Create new import
            new_import = ast.ImportFrom(
                module='agentic_core.L0_routing.config.path_constants',
                names=[ast.alias(name='THRESHOLD', asname=None)],
                level=0,
            )

            # Insert after last import
            node.body.insert(last_import_idx, new_import)
            self.added_import = True

        return node


def fix_file(file_path: Path, dry_run: bool = True) -> dict:
    """Fix a single file using AST transformation."""
    try:
        # Skip if this is path_constants.py itself
        if file_path.name == 'path_constants.py' and 'L0_routing' in str(file_path):
            return {'status': 'skipped', 'reason': 'ssot_source'}

        source = file_path.read_text(encoding='utf-8')

        # Parse AST
        tree = ast.parse(source, filename=str(file_path))

        # Transform threshold values
        transformer = ThresholdTransformer()
        tree = transformer.visit(tree)

        if not transformer.modified:
            return {'status': 'skipped', 'reason': 'no_modifications'}

        # Add import if modifications were made
        import_adder = ImportAdder()
        tree = import_adder.visit(tree)

        # Fix missing locations for new nodes
        ast.fix_missing_locations(tree)

        # Generate new source
        new_source = ast.unparse(tree)

        if not dry_run:
            file_path.write_text(new_source, encoding='utf-8')

        return {
            'status': 'success',
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'modifications': len(transformer.modifications),
            'added_import': import_adder.added_import,
            'dry_run': dry_run,
        }

    except SyntaxError as e:
        return {
            'status': 'error',
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'error': f'SyntaxError: {e}',
        }
    except Exception as e:
        return {
            'status': 'error',
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'error': str(e),
        }


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(description='AST-based threshold fixer')
    parser.add_argument('--execute', action='store_true', help='Actually write changes')
    parser.add_argument('--limit', type=int, default=50, help='Max files to process')
    parser.add_argument('--file', type=str, help='Fix specific file')

    args = parser.parse_args()

    project_root = get_validated_project_root()

    if args.file:
        # Fix specific file
        file_path = project_root / args.file
        if not file_path.exists():
            print(f"[ERROR] File not found: {file_path}")
            return 1

        result = fix_file(file_path, dry_run=not args.execute)

        if result['status'] == 'success':
            print(f"✓ {result['file']}")
            print(f"  Modifications: {result['modifications']}")
            print(f"  Added import: {result['added_import']}")
        elif result['status'] == 'error':
            print(f"✗ {result['file']}: {result['error']}")
        else:
            print(f"- {result.get('file', args.file)}: {result['reason']}")

        return 0

    # Batch mode
    baseline_file = project_root / "ops_scripts" / "hooks" / "landmine_baseline.txt"

    violations = []
    with open(baseline_file, 'r', encoding='utf-8') as f:
        for line in f:
            if 'threshold=0.95' in line:
                file_path = line.split(':')[0]
                violations.append(project_root / file_path)

    unique_files = sorted(set(violations))[:args.limit]

    print(f"[INFO] Processing {len(unique_files)} files")
    print(f"[MODE] {'EXECUTE' if args.execute else 'DRY RUN'}")
    print()

    results = []
    for file_path in unique_files:
        if not file_path.exists():
            continue

        result = fix_file(file_path, dry_run=not args.execute)
        results.append(result)

        if result['status'] == 'success':
            print(f"✓ {result['file']}")
        elif result['status'] == 'error':
            print(f"✗ {result['file']}: {result['error']}")

    success = len([r for r in results if r['status'] == 'success'])
    errors = len([r for r in results if r['status'] == 'error'])
    skipped = len([r for r in results if r['status'] == 'skipped'])

    print()
    print(f"[SUMMARY] Success: {success}, Errors: {errors}, Skipped: {skipped}")

    if not args.execute and success > 0:
        print("[NEXT] Run with --execute to apply changes")

    return 0


if __name__ == '__main__':
    sys.exit(main())
