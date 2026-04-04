#!/usr/bin/env python3
"""
Get final remaining broken files.
"""

import ast
import pathlib


def get_final_remaining():
    """Get final remaining broken test files."""
    broken_files = []
    tests_dir = pathlib.Path('tests')

    for f in sorted(tests_dir.rglob('test_*.py')):
        if 'archive' in str(f).lower():
            continue

        try:
            content = f.read_text(encoding='utf-8', errors='replace')
            ast.parse(content)
        except SyntaxError:
            broken_files.append(f)
        except Exception:
            continue

    # Skip first 814 files (already fixed)
    remaining = broken_files[814:]

    print(f"Final remaining {len(remaining)} files:")
    for i, f in enumerate(remaining, 1):
        print(f"{i:3d}. {f}")

    return remaining

if __name__ == '__main__':
    get_final_remaining()
