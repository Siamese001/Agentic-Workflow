#!/usr/bin/env python3
"""Delete unused functions from Python files."""

import argparse
import ast
import json
import sys
from pathlib import Path


def remove_function(file_path: str, func_name: str) -> bool:
    """Remove a specific function from a Python file."""
    path = Path(file_path)
    if not path.exists():
        return False
    
    try:
        source = path.read_text(encoding='utf-8')
        lines = source.split('\n')
    except Exception:
        return False
    
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    
    # Find function node
    target_node = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == func_name:
            target_node = node
            break
    
    if not target_node:
        return False
    
    start_line = target_node.lineno
    end_line = target_node.end_lineno
    
    # Remove the function
    new_lines = lines[:start_line - 1] + lines[end_line:]
    path.write_text('\n'.join(new_lines), encoding='utf-8')
    print(f"  Removed {func_name} from {file_path} (lines {start_line}-{end_line})")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--limit', type=int)
    
    args = parser.parse_args()
    
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    funcs = data.get('unused_functions', [])
    if args.limit:
        funcs = funcs[:args.limit]
    
    print(f'Processing {len(funcs)} unused functions...')
    
    deleted = 0
    for func in funcs:
        file_path = func['file']
        func_name = func['name']
        
        if args.dry_run:
            print(f"[DRY-RUN] Would delete {func_name} from {file_path}")
            deleted += 1
        else:
            if remove_function(file_path, func_name):
                deleted += 1
    
    print(f'\n{"Would delete" if args.dry_run else "Deleted"} {deleted} functions')
    return 0


if __name__ == '__main__':
    sys.exit(main())
