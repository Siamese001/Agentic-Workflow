#!/usr/bin/env python3
"""Remove unused imports from Python files using ADG analysis."""

import argparse
import ast
import json
import sys
from pathlib import Path


def remove_unused_imports(file_path: str, imports_to_remove: list[str]) -> bool:
    """Remove specific unused imports from a Python file."""
    path = Path(file_path)
    if not path.exists():
        print(f"  File not found: {file_path}")
        return False
    
    try:
        source = path.read_text(encoding='utf-8')
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"  Syntax error in {file_path}: {e}")
        return False
    
    # Find import lines to remove
    lines_to_remove = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for target in imports_to_remove:
                # Match various import patterns
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        full_name = alias.name
                        if alias.asname:
                            full_name += f" as {alias.asname}"
                        if target in full_name or alias.name in target:
                            lines_to_remove.add(node.lineno)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        full_name = f"{module}.{alias.name}" if module else alias.name
                        if target in full_name or alias.name in target:
                            lines_to_remove.add(node.lineno)
    
    if not lines_to_remove:
        print(f"  No matching imports found in {file_path}")
        return False
    
    # Remove lines
    lines = source.split('\n')
    new_lines = [line for i, line in enumerate(lines, 1) if i not in lines_to_remove]
    
    # Write back
    path.write_text('\n'.join(new_lines), encoding='utf-8')
    print(f"  Removed {len(lines_to_remove)} imports from {file_path}")
    return True


def process_targets(targets: list[dict], directory: str | None = None) -> tuple[int, int]:
    """Process import removal targets."""
    # Group by file
    files_imports: dict[str, list[str]] = {}
    
    for target in targets:
        file_path = target.get('source_file', '')
        if directory and directory not in file_path:
            continue
        
        symbol = target.get('symbol', '')
        if file_path not in files_imports:
            files_imports[file_path] = []
        files_imports[file_path].append(symbol)
    
    # Process each file
    modified = 0
    total = 0
    for file_path, imports in files_imports.items():
        print(f"Processing {file_path}...")
        if remove_unused_imports(file_path, imports):
            modified += 1
        total += 1
    
    return modified, total


def main():
    parser = argparse.ArgumentParser(description='Remove unused imports from Python files')
    parser.add_argument('--input', required=True, help='JSON file with targets')
    parser.add_argument('--directory', help='Filter to specific directory')
    parser.add_argument('--dry-run', action='store_true', help='Preview without executing')
    
    args = parser.parse_args()
    
    with open(args.input, 'r', encoding='utf-8') as f:
        targets = json.load(f)
    
    if args.dry_run:
        # Preview mode
        files_imports: dict[str, list[str]] = {}
        for target in targets:
            file_path = target.get('source_file', '')
            if args.directory and args.directory not in file_path:
                continue
            symbol = target.get('symbol', '')
            if file_path not in files_imports:
                files_imports[file_path] = []
            files_imports[file_path].append(symbol)
        
        print(f"[DRY-RUN] Would process {len(files_imports)} files:")
        for file_path, imports in list(files_imports.items())[:10]:
            print(f"  {file_path}: {len(imports)} imports")
        if len(files_imports) > 10:
            print(f"  ... and {len(files_imports) - 10} more files")
        return 0
    
    # Execute
    modified, total = process_targets(targets, args.directory)
    print(f"\nModified {modified} of {total} files")
    return 0


if __name__ == '__main__':
    sys.exit(main())
