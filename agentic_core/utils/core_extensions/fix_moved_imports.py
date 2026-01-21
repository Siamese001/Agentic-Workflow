from __future__ import annotations

"""
Fix imports after moving files to P1_core subdirectories.
Updates all references to moved files throughout the codebase.
"""
import re
from pathlib import Path
from typing import Any

root: Any = Path('C:/Git/Agentic-Workflow')
import_rewrites: Any = {'from \\.fission_executor import': 'from .P1_core.fission_executor import'}

def fix_imports() -> Any:
    """Fix all imports referencing moved files."""
    print('[*] FIXING IMPORTS AFTER FILE MOVES...')
    fixed: Any = 0
    # Phase 6.8: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files
    for py_file in get_python_files(ROOT):
        try:
            content: Any = py_file.read_text(encoding='utf-8')
            original: Any = content
            for old_pattern, new_path in IMPORT_REWRITES.items():
                content: Any = re.sub(old_pattern, new_path, content)
            if content != original:
                py_file.write_text(content, encoding='utf-8')
                print(f'  [✓] Fixed: {py_file.relative_to(ROOT)}')
                fixed += 1
        except Exception:
            pass
    print(f'\n[OK] Fixed {fixed} import statements')
if __name__ == '__main__':
    fix_imports()
