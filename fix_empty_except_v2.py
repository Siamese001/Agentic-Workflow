#!/usr/bin/env python
"""Fix all empty except blocks in smoke test files."""

from pathlib import Path


def fix_empty_except_blocks():
    smoke_dir = Path('tests/smoke')
    for py_file in smoke_dir.rglob('*.py'):
        content = py_file.read_text(encoding='utf-8')
        lines = content.split('\n')
        new_lines = []
        i = 0
        changed = False

        while i < len(lines):
            line = lines[i]
            new_lines.append(line)

            # Check for empty except blocks
            if 'except ImportError as e:' in line:
                # Count leading spaces for indentation
                indent = len(line) - len(line.lstrip())

                # Look ahead for empty lines followed by non-empty content
                j = i + 1
                empty_count = 0
                while j < len(lines) and lines[j].strip() == '':
                    empty_count += 1
                    j += 1

                # If we found empty lines and the next line has less or equal indentation,
                # it's likely an empty except block
                if empty_count >= 2 and j < len(lines):
                    next_line = lines[j]
                    if next_line and len(next_line) - len(next_line.lstrip()) <= indent + 4:
                        # Add pytest.skip with proper indentation
                        skip_line = ' ' * (indent + 4) + 'pytest.skip(f"module not available: {e}")'
                        new_lines.append(skip_line)
                        # Skip the empty lines
                        i = j - 1
                        changed = True

            i += 1

        if changed:
            py_file.write_text('\n'.join(new_lines), encoding='utf-8')
            print(f'Fixed {py_file.relative_to(smoke_dir)}')

if __name__ == '__main__':
    fix_empty_except_blocks()
