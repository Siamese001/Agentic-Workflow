#!/usr/bin/env python3
"""AST-based analysis to find unused test functions."""

import ast
import json
import sqlite3
from pathlib import Path


def find_test_functions(file_path: Path) -> list[dict]:
    """Parse a test file and find all test function definitions."""
    try:
        source = file_path.read_text(encoding='utf-8')
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError):
        return []

    test_funcs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check if it's a test function (starts with test_)
            if node.name.startswith('test_'):
                test_funcs.append({
                    'name': node.name,
                    'line': node.lineno,
                    'file': str(file_path),
                })
    return test_funcs


def find_unused_test_functions(directory: str, adg_db_path: Path) -> list[dict]:
    """Find test functions that are never called (not just test discovery)."""
    conn = sqlite3.connect(adg_db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    unused_tests = []

    # Get all test functions from AST
    dir_path = Path(directory)
    for test_file in dir_path.rglob('test_*.py'):
        funcs = find_test_functions(test_file)

        for func in funcs:
            # Check if this function has any 'calls' edges TO it
            # In ADG, test functions are called by pytest's test runner
            # If there are NO incoming edges at all, it's truly unused
            func_name = func['name']
            file_path = func['file']

            # Query ADG for any edges pointing to this function
            c.execute('''
                SELECT COUNT(*) as call_count
                FROM edges e
                JOIN nodes n ON e.dst_id = n.id
                WHERE n.resolved_path = ?
                AND n.adg_name LIKE ?
                AND e.relation_type IN ('calls', 'tests_execution_of')
            ''', (file_path, f'%{func_name}%'))

            result = c.fetchone()
            if result and result['call_count'] == 0:
                func['reason'] = 'No ADG call edges found'
                unused_tests.append(func)

    conn.close()
    return unused_tests


def main():
    dbs = sorted(Path('artifacts/adg').glob('adg_indexed_*.sqlite'))
    if not dbs:
        print('No ADG databases found')
        return 1

    adg_db = dbs[-1]
    print(f'Using ADG: {adg_db}')

    # Analyze tests/adg/ directory
    print('\nAnalyzing tests/adg/ for unused test functions...')
    unused = find_unused_test_functions('tests/adg', adg_db)

    print(f'\nFound {len(unused)} potentially unused test functions:')
    for test in unused[:20]:
        print(f"  {test['file']}:{test['line']} - {test['name']}")

    if len(unused) > 20:
        print(f"  ... and {len(unused) - 20} more")

    # Save to JSON
    output = {
        'adg_database': str(adg_db),
        'directory': 'tests/adg',
        'unused_tests': unused,
    }

    output_path = Path('wave1_ast_unused_tests.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f'\nResults saved to: {output_path}')
    return 0


if __name__ == '__main__':
    exit(main())
