#!/usr/bin/env python3
"""Delete unused test functions from Python files."""

import argparse
import ast
import json
import sys
from pathlib import Path


def remove_test_function(file_path: str, func_name: str) -> bool:
    """Remove a specific test function from a Python file."""
    path = Path(file_path)
    if not path.exists():
        return False
    
    try:
        source = path.read_text(encoding='utf-8')
        lines = source.split('\n')
    except (OSError, IOError) as e:
        print(f"  Error reading {file_path}: {e}")
        return False
    
    # Parse to find function boundaries
    try:
        tree = ast.parse(source)
    except SyntaxError:
        print(f"  Syntax error in {file_path}")
        return False
    
    # Find the function node
    target_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            target_node = node
            break
    
    if not target_node:
        print(f"  Function {func_name} not found in {file_path}")
        return False
    
    # Get line range (1-indexed)
    start_line = target_node.lineno
    end_line = target_node.end_lineno
    
    # Remove the function (and following blank lines)
    new_lines = lines[:start_line - 1] + lines[end_line:]
    
    # Write back
    path.write_text('\n'.join(new_lines), encoding='utf-8')
    print(f"  Removed {func_name} from {file_path} (lines {start_line}-{end_line})")
    return True


def main():
    parser = argparse.ArgumentParser(description='Delete unused test functions')
    parser.add_argument('--input', required=True, help='JSON file with test functions to delete')
    parser.add_argument('--dry-run', action='store_true', help='Preview without deleting')
    parser.add_argument('--limit', type=int, help='Limit number of deletions')
    
    args = parser.parse_args()
    
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tests = data.get('unused_tests', [])
    if args.limit:
        tests = tests[:args.limit]
    
    print(f'Processing {len(tests)} unused test functions...')
    
    deleted = 0
    for test in tests:
        file_path = test['file']
        func_name = test['name']
        
        if args.dry_run:
            print(f"[DRY-RUN] Would delete {func_name} from {file_path}")
            deleted += 1
        else:
            if remove_test_function(file_path, func_name):
                deleted += 1
    
    print(f'\n{"Would delete" if args.dry_run else "Deleted"} {deleted} test functions')
    return 0


if __name__ == '__main__':
    sys.exit(main())
