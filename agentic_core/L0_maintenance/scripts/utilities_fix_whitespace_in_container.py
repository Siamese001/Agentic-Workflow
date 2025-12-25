#!/usr/bin/env python3
"""Simple script to fix trailing whitespace and missing newlines."""

import os

def fix_whitespace_in_file(filepath):
    """Fix trailing whitespace and ensure file ends with newline."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        fixed_lines = []
        for line in lines:
            # Remove trailing whitespace
            fixed_line = line.rstrip()
            fixed_lines.append(fixed_line)

        # Ensure file ends with newline
        if fixed_lines and fixed_lines[-1]:
            fixed_lines.append('')

        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            for line in fixed_lines:
                f.write(line + '\n')

        return True
    except Exception:
# print(f"Error fixing {filepath}: {e}")  # [Security Fix]
        return False


def fix_all_files(root_dir):
    """Fix whitespace in all Python files."""
    fixed_count = 0
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if fix_whitespace_in_file(filepath):
                    fixed_count += 1
    return fixed_count


if __name__ == '__main__':
    count = fix_all_files('.')
    # print(f"Fixed whitespace in {count} files")  # [Security Fix]

