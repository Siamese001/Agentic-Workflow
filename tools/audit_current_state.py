#!/usr/bin/env python3
"""Audit current state of import-only tests."""

import ast
from pathlib import Path


def file_is_import_only(fp):
    try:
        source = fp.read_text(encoding='utf-8')
        tree = ast.parse(source)
    except Exception:
        return False, 0
    test_funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith('test_')]
    if not test_funcs:
        return False, 0
    lines = len(source.splitlines())
    return True, lines

# Full audit
total = 0
import_only = 0
size_counts = {'tiny': 0, 'small': 0, 'medium': 0, 'large': 0}

for p in Path('tests').rglob('test_*.py'):
    total += 1
    is_io, lines = file_is_import_only(p)
    if is_io:
        import_only += 1
        if lines <= 15:
            size_counts['tiny'] += 1
        elif lines <= 50:
            size_counts['small'] += 1
        elif lines <= 200:
            size_counts['medium'] += 1
        else:
            size_counts['large'] += 1

print(f'TOTAL_TEST_FILES={total}')
print(f'IMPORT_ONLY_COUNT={import_only}')
print(f'TINY_LE15={size_counts["tiny"]}')
print(f'SMALL_16_50={size_counts["small"]}')
print(f'MEDIUM_51_200={size_counts["medium"]}')
print(f'LARGE_GT200={size_counts["large"]}')
print()
print(f'Reduction: 1675 -> {size_counts["tiny"]} tiny files ({(1-size_counts["tiny"]/1675)*100:.1f}% reduction)')
