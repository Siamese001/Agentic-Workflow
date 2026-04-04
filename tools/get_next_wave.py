#!/usr/bin/env python3
"""
Get the next wave of broken files for processing.
"""

import ast
import pathlib


def get_next_wave(wave_num: int, count: int = 7):
    """Get the next wave of broken files."""
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
        except:
            continue

    start_idx = (wave_num - 1) * count
    end_idx = start_idx + count
    wave_files = broken_files[start_idx:end_idx]

    print(f"Wave {wave_num} files ({len(wave_files)}):")
    for i, f in enumerate(wave_files, 1):
        print(f"{i}. {f}")

    return wave_files

if __name__ == '__main__':
    import sys
    wave = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    get_next_wave(wave, count)
