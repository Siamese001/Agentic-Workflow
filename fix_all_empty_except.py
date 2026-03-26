#!/usr/bin/env python
"""Fix all empty except blocks in smoke test files."""

import re
from pathlib import Path


def fix_all_empty_except():
    smoke_dir = Path('tests/smoke')
    for py_file in smoke_dir.rglob('*.py'):
        content = py_file.read_text(encoding='utf-8')

        # Pattern to match empty except blocks
        # except ImportError as e:\n\n\n    <next_line>
        pattern = r'(except ImportError as e:\n)\n\n(\n    [^\s])'

        def replacement(match):
            except_line = match.group(1)
            next_line = match.group(2)
            # Add pytest.skip
            return f'{except_line}        pytest.skip(f"module not available: {{e}}")\n{next_line}'

        new_content = re.sub(pattern, replacement, content)

        if new_content != content:
            py_file.write_text(new_content, encoding='utf-8')
            print(f'Fixed {py_file.relative_to(smoke_dir)}')

if __name__ == '__main__':
    fix_all_empty_except()
