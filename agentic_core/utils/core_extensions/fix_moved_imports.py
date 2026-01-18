from __future__ import annotations
"""
Fix imports after moving files to P1_core subdirectories.
Updates all references to moved files throughout the codebase.
"""
import re
from pathlib import Path
from typing import Any
from agentic_core.utils.sovereign_index import SovereignIndex
root: Any = Path('C:/Git/Agentic-Workflow')
import_rewrites: Any = {'from \\.fission_executor import': 'from .P1_core.fission_executor import'}

def fix_imports() -> Any:
    """Fix all imports referencing moved files."""
    print('[*] FIXING IMPORTS AFTER FILE MOVES...')
    fixed: Any = 0
    for py_file in ROOT.rglob('*.py'):
        if 'venv' in str(py_file) or '.git' in str(py_file):
            continue
        try:
            content: Any = py_file.read_text(encoding='utf-8')
            original: Any = content
            for old_pattern, new_path in IMPORT_REWRITES.items():
                content: Any = re.sub(old_pattern, new_path, content)
            if content != original:
                py_file.write_text(content, encoding='utf-8')
                print(f'  [✓] Fixed: {py_file.relative_to(ROOT)}')
                fixed += 1
        except Exception as e:
            pass
    print(f'\n[OK] Fixed {fixed} import statements')
if __name__ == '__main__':
    fix_imports()
