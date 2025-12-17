#!/usr/bin/env python3
"""
Fix split string literals across multiple Python files.
This script fixes the common pattern where string literals were incorrectly
split across lines without proper line continuation.
"""

import sys
from pathlib import Path


def fix_split_strings_in_file(filepath):
    """Fix split string literals in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        lines = content.split('\n')
        fixed_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check if line ends with an unclosed string literal
            # Pattern: ends with quote but doesn't have closing quote for the string
            if line.strip():
                # Count quotes to detect unclosed strings
                quote_count = line.count('"') + line.count("'")

                # If odd number of quotes, we have an unclosed string
                if quote_count % 2 == 1:
                    # Look ahead to find the continuation
                    j = i + 1
                    continuation_lines = []

                    while j < len(lines):
                        next_line = lines[j]
                        if next_line.strip():
                            next_quote_count = next_line.count(
                                '"') + next_line.count("'")
                            if next_quote_count > 0:
                                # Join the lines properly
                                fixed_line = line.rstrip() + ' ' + next_line.lstrip()
                                fixed_lines.append(fixed_line)
                                i = j  # Skip the next line as we've merged it
                                break
                            else:
                                continuation_lines.append(next_line)
                        j += 1

                    if j >= len(lines):
                        # No continuation found, keep original
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

            i += 1

        fixed_content = '\n'.join(fixed_lines)

        # Write back if changed
        if fixed_content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True

        return False

    except Exception as e:
pass
# print(f"Error processing {filepath}: {e}")  # [Security Fix]
        return False


def fix_all_python_files(root_dir):
    """Fix split strings in all Python files under root_dir."""
    root_path = Path(root_dir)
    fixed_count = 0

    # Focus on directories with syntax errors
    target_dirs = [
        'agentic_core',
        '16_runtime_runtime',
        '19_runtime_pipeline'
    ]

    for target_dir in target_dirs:
        dir_path = root_path / target_dir
        if dir_path.exists():
            # print(f"\nProcessing directory: {target_dir}")  # [Security Fix]
            for py_file in dir_path.rglob('*.py'):
                if fix_split_strings_in_file(py_file):
                    # print(f"  Fixed: {py_file.relative_to(root_path)}")  # [Security Fix]
                    fixed_count += 1

    # print(f"\nTotal files fixed: {fixed_count}")  # [Security Fix]


if __name__ == '__main__':
    root_dir = '.' if len(sys.argv) < 2 else sys.argv[1]
    fix_all_python_files(root_dir)

