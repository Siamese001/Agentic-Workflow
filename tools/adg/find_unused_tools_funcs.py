#!/usr/bin/env python3
"""AST-based analysis to find unused functions in tools/ directory."""

import ast
import json
import sqlite3
from pathlib import Path


def find_functions_in_file(file_path: Path) -> list[dict]:
    """Parse a Python file and find all function/class definitions."""
    try:
        source = file_path.read_text(encoding='utf-8')
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError):
        return []

    funcs = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            # Skip private functions (leading underscore)
            if not node.name.startswith('_'):
                funcs.append({
                    'name': node.name,
                    'line': node.lineno,
                    'file': str(file_path),
                    'type': type(node).__name__
                })
    return funcs


def find_unused_functions(directory: str, adg_db_path: Path) -> list[dict]:
    """Find functions that are never called."""
    conn = sqlite3.connect(adg_db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    unused_funcs = []
    dir_path = Path(directory)

    for py_file in dir_path.rglob('*.py'):
        # Skip test files
        if 'test' in py_file.name:
            continue

        funcs = find_functions_in_file(py_file)

        for func in funcs:
            func_name = func['name']
            file_path = func['file']

            # Check if this function has any 'calls' edges TO it
            c.execute('''
                SELECT COUNT(*) as call_count
                FROM edges e
                JOIN nodes n ON e.dst_id = n.id
                WHERE n.resolved_path = ?
                AND n.adg_name LIKE ?
                AND e.relation_type = 'calls'
            ''', (file_path, f'%{func_name}%'))

            result = c.fetchone()
            if result and result['call_count'] == 0:
                func['reason'] = 'No ADG call edges found'
                unused_funcs.append(func)

    conn.close()
    return unused_funcs


def main():
    dbs = sorted(Path('artifacts/adg').glob('adg_indexed_*.sqlite'))
    if not dbs:
        print('No ADG databases found')
        return 1

    adg_db = dbs[-1]
    print(f'Using ADG: {adg_db}')

    # Analyze tools/ directory
    print('\nAnalyzing tools/ for unused functions...')
    unused = find_unused_functions('tools', adg_db)

    print(f'\nFound {len(unused)} potentially unused functions:')
    for func in unused[:30]:
        print(f"  {func['file']}:{func['line']} - {func['name']} ({func['type']})")

    if len(unused) > 30:
        print(f"  ... and {len(unused) - 30} more")

    # Save to JSON
    output = {
        'adg_database': str(adg_db),
        'directory': 'tools',
        'unused_functions': unused
    }

    output_path = Path('wave2_tools_unused_funcs.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f'\nResults saved to: {output_path}')
    return 0


if __name__ == '__main__':
    exit(main())
