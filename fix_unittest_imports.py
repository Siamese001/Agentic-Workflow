#!/usr/bin/env python3
"""Fix missing unittest imports in test files."""

import pathlib
import sys

def fix_unittest_import(file_path: pathlib.Path) -> bool:
    """Add missing unittest import to test files."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'unittest' not in content and 'NameError: name \'unittest\'' in content:
            # Add unittest import after the first import line
            lines = content.split('\n')
            new_lines = []
            added = False
            
            for line in lines:
                new_lines.append(line)
                if line.startswith('import ') or line.startswith('from '):
                    if not added and 'unittest' not in line:
                        new_lines.append('import unittest')
                        added = True
            
            content = '\n'.join(new_lines)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}", file=sys.stderr)
        return False

def main():
    """Fix all files missing unittest imports."""
    import glob
    
    # Find all test files that might need unittest import
    test_files = glob.glob('tests/unit/agentic_core/L0_routing/types/test_*.py')
    
    fixed_count = 0
    for file_path in test_files:
        path = pathlib.Path(file_path)
        if fix_unittest_import(path):
            print(f"Fixed: {file_path}")
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    main()
