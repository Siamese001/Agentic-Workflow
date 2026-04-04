#!/usr/bin/env python3
"""Recheck all waves for import-only test elimination."""

import ast
import re
from pathlib import Path


def extract_module_from_source(source):
    lines = source.splitlines()
    for line in lines:
        if 'import ' in line and 'noqa: F401' in line:
            match = re.search(r'import\s+([^\s]+)', line)
            if match:
                return match.group(1)
        elif 'import ' in line and ' as _mod' in line:
            match = re.search(r'import\s+([^\s]+)\s+as\s+_mod', line)
            if match:
                return match.group(1)
    return None

def is_truly_import_only(source):
    try:
        tree = ast.parse(source)
    except:
        return False
    test_funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith('test_')]
    if not test_funcs:
        return False

    # Check if tests have actual assertions or just pass
    for func in test_funcs:
        for node in ast.walk(func):
            if isinstance(node, ast.Assert):
                return False  # Has assertions
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'skip':
                return False  # Has skips
            if isinstance(node, ast.Pass):
                continue  # pass statements are OK for import-only

    return True

# Comprehensive audit
total = 0
import_only = 0
size_counts = {'tiny': 0, 'small': 0, 'medium': 0, 'large': 0}
samples = {'tiny': [], 'small': [], 'medium': [], 'large': []}

for p in Path('tests').rglob('test_*.py'):
    total += 1
    try:
        source = p.read_text(encoding='utf-8')
        lines = len(source.splitlines())
        module_path = extract_module_from_source(source)

        if module_path and is_truly_import_only(source):
            import_only += 1
            if lines <= 15:
                size_counts['tiny'] += 1
                if len(samples['tiny']) < 5:
                    samples['tiny'].append((str(p), module_path, lines))
            elif lines <= 50:
                size_counts['small'] += 1
                if len(samples['small']) < 5:
                    samples['small'].append((str(p), module_path, lines))
            elif lines <= 200:
                size_counts['medium'] += 1
                if len(samples['medium']) < 5:
                    samples['medium'].append((str(p), module_path, lines))
            else:
                size_counts['large'] += 1
                if len(samples['large']) < 5:
                    samples['large'].append((str(p), module_path, lines))
    except:
        pass

print('=== COMPREHENSIVE RECHECK OF ALL WAVES ===')
print(f'TOTAL_TEST_FILES={total}')
print(f'TRULY_IMPORT_ONLY={import_only}')
print()
print('BY SIZE:')
print(f'TINY_LE15={size_counts["tiny"]}')
print(f'SMALL_16_50={size_counts["small"]}')
print(f'MEDIUM_51_200={size_counts["medium"]}')
print(f'LARGE_GT200={size_counts["large"]}')
print()

for size, label in [('tiny', 'Tiny (≤15)'), ('small', 'Small (16-50)'), ('medium', 'Medium (51-200)'), ('large', 'Large (>200)')]:
    if size_counts[size] > 0:
        print(f'{label} - {size_counts[size]} files:')
        for fp, mp, lines in samples[size]:
            print(f'  {fp} ({lines} lines) -> {mp}')
        print()
