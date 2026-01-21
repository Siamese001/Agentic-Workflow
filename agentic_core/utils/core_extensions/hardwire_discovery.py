from __future__ import annotations

'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import re
from pathlib import Path
from typing import Any

root: Any = Path('C:/Git/Agentic-Workflow/agentic_core')
path_redirects: Any = {}

def hardwire_discovery() -> Any:
    """Brief description of functionality and purpose."""
    print('[*] HARDWIRING DISCOVERY SYNAPSES...')
    fixed: Any = 0
    # Phase 6.8: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files
    for py_file in get_python_files(ROOT):
        try:
            content: Any = py_file.read_text(encoding='utf-8')
            original: Any = content
            for old, new in PATH_REDIRECTS.items():
                content: Any = re.sub(old, new, content)
            if '_types.py' in py_file.name and 'Enum' in content and ('from enum import Enum' not in content):
                content: Any = 'from enum import Enum\n' + content
            if content != original:
                py_file.write_text(content, encoding='utf-8')
                print(f'  [✓] Synapse Anchored: {py_file.relative_to(ROOT)}')
                fixed += 1
        except Exception:
            pass
    print(f'\n[OK] DISCOVERY FIXED. {fixed} files anchored.')
if __name__ == '__main__':
    hardwire_discovery()
