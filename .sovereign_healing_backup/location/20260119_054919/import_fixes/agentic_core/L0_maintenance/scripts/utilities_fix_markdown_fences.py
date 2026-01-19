from __future__ import annotations
"""
Fix markdown code fences in Python files.
Removes ```python and ``` from files that have them.
"""
import re
from pathlib import Path
from typing import Any
from agentic_core.utils.sovereign_index import SovereignIndex
from archives.location_violations.file_utils import safe_read_file, safe_write_file

def fix_markdown_fences(file_path: str) -> bool:
    """Remove markdown code fences from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content: Any = f.read()
        if '```python' not in content and '```' not in content:
            return False
        content: Any = re.sub('^```python\\s*\\n', '', content, flags=re.MULTILINE)
        content: Any = re.sub('\\n```\\s*$', '', content)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'✅ Fixed: {file_path}')
        return True
    except Exception as e:
        print(f'❌ Error fixing {file_path}: {e}')
        return False

def main() -> Any:
    """Find and fix all Python files with markdown fences."""
    root: Any = Path('c:/Git/Agentic-Workflow/agentic_core')
    fixed_count: Any = 0
    for py_file in root.rglob('*.py'):
        if fix_markdown_fences(str(py_file)):
            fixed_count += 1
    print(f'\n🎯 Fixed {fixed_count} files')
if __name__ == '__main__':
    main()
