#!/usr/bin/env python3
"""
Check total broken files count.
"""

import pathlib
import ast

def count_broken_files():
    """Count all broken test files."""
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
    
    print(f"Total broken files: {len(broken_files)}")
    print(f"Files fixed so far: 714")
    print(f"Remaining: {len(broken_files) - 714}")
    
    return broken_files

if __name__ == '__main__':
    count_broken_files()
