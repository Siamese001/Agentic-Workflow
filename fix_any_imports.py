"""Fix missing Any imports in test files."""
import os
import re
from pathlib import Path

tests_dir = Path('tests')
fixed = 0

# Pattern to detect Any usage - check word boundary
any_usage_pattern = re.compile(r'\bAny\b')

for py_file in tests_dir.rglob('*.py'):
    try:
        content = py_file.read_text(encoding='utf-8')
        # Check if file uses Any but doesn't import it
        uses_any = bool(any_usage_pattern.search(content))
        if uses_any:
            if 'from typing import Any' in content or 'import Any' in content:
                continue  # Already has import
            if 'from typing import' in content:
                # Add Any to existing typing import
                def add_any(m):
                    imports = m.group(1)
                    if 'Any' not in imports:
                        return f'from typing import Any, {imports}'
                    return m.group(0)
                content = re.sub(r'from typing import ([^\n]+)', add_any, content, count=1)
                py_file.write_text(content, encoding='utf-8')
                fixed += 1
                print(f'Fixed (added to existing): {py_file}')
            else:
                # Add new import after docstring or first imports
                lines = content.split('\n')
                insert_idx = 0
                in_docstring = False
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith('"""') or stripped.startswith("'''"):
                        if in_docstring:
                            in_docstring = False
                            insert_idx = i + 1
                        else:
                            in_docstring = True
                        continue
                    if in_docstring:
                        continue
                    if stripped.startswith('import ') or stripped.startswith('from '):
                        insert_idx = i + 1
                
                if insert_idx > 0:
                    lines.insert(insert_idx, 'from typing import Any')
                    py_file.write_text('\n'.join(lines), encoding='utf-8')
                    fixed += 1
                    print(f'Fixed (new import): {py_file}')
    except Exception as e:
        print(f'Error {py_file}: {e}')

print(f'\nTotal fixed: {fixed}')
