#!/usr/bin/env python3
"""
Get next wave of remaining broken files.
"""

import ast
import pathlib


def get_next_wave_remaining(wave_num, count):
    """Get next wave of remaining broken files."""
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

    # Skip first 714 files (already fixed)
    remaining = broken_files[714:]

    # Get next wave
    start = (wave_num - 10) * count  # Wave 10 starts at index 0
    end = start + count
    wave_files = remaining[start:end]

    print(f"Wave {wave_num} files ({len(wave_files)}):")
    for i, f in enumerate(wave_files, 1):
        print(f"  {i:3d}. {f}")

    return wave_files

if __name__ == '__main__':
    import sys
    wave = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    get_next_wave_remaining(wave, count)
