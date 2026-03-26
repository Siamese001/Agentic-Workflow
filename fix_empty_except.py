#!/usr/bin/env python
"""Fix empty except blocks in smoke test files."""

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
                # Look ahead for empty lines
                j = i + 1
                empty_lines = 0
                while j < len(lines) and lines[j].strip() == '':
                    empty_lines += 1
                    j += 1
                # If next non-empty line is a decorator, function, or end of file, it's an empty except block
                if j >= len(lines) or lines[j].startswith('@pytest') or lines[j].startswith('def ') or lines[j].startswith('class ') or lines[j].startswith('if ') or lines[j].startswith('#'):
                    # Add pytest.skip
                    indent = len(line) - len(line.lstrip())
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
