"""Bulk fix script for test syntax errors - removes misplaced imports inside functions."""
import re
from pathlib import Path

tests_dir = Path('tests')
fixed_count = 0

# Pattern to find imports inside function bodies (after docstring)
misplaced_import_pattern = re.compile(
    r'("""[^"]*"""\s*\n)(from typing import Any\n)(\s+)',
    re.MULTILINE
)

for py_file in tests_dir.rglob('*.py'):
    try:
        content = py_file.read_text(encoding='utf-8')
        original = content
        
        # Fix 1: Remove misplaced "from typing import Any" inside functions
        # Pattern: docstring followed by import on next line with wrong indentation
        lines = content.split('\n')
        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # Check if this is a misplaced import (not at top level, starts with "from typing")
            stripped = line.strip()
            if stripped == 'from typing import Any':
                # Check if previous non-empty line ends with : or """ (function/docstring)
                prev_idx = i - 1
                while prev_idx >= 0 and not lines[prev_idx].strip():
                    prev_idx -= 1
                if prev_idx >= 0:
                    prev_stripped = lines[prev_idx].strip()
                    # If previous line is docstring end or function start, this is misplaced
                    if prev_stripped.endswith('"""') or prev_stripped.endswith("'''"):
                        # Skip this misplaced import
                        i += 1
                        continue
            new_lines.append(line)
            i += 1
        
        content = '\n'.join(new_lines)
        
        # Fix 2: Ensure Any import exists at top if Any is used
        if re.search(r'\bAny\b', content):
            if 'from typing import Any' not in content and 'from typing import' in content:
                # Add Any to existing typing import
                content = re.sub(
                    r'from typing import ([^\n]+)',
                    lambda m: f'from typing import Any, {m.group(1)}' if 'Any' not in m.group(1) else m.group(0),
                    content,
                    count=1
                )
            elif 'from typing import Any' not in content and 'from typing import' not in content:
                # Add new import after other imports
                lines = content.split('\n')
                insert_idx = 0
                for idx, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith('import ') or stripped.startswith('from '):
                        insert_idx = idx + 1
                if insert_idx > 0:
                    lines.insert(insert_idx, 'from typing import Any')
                    content = '\n'.join(lines)
        
        if content != original:
            py_file.write_text(content, encoding='utf-8')
            fixed_count += 1
            print(f'Fixed: {py_file}')
            
    except Exception as e:
        print(f'Error {py_file}: {e}')

print(f'\nTotal fixed: {fixed_count}')
