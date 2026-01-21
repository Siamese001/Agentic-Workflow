from __future__ import annotations

'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import re
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENTIC_CORE_DIR,
)

root: Any = Path('C:/Git/Agentic-Workflow')
core: Any = ROOT / AGENTIC_CORE_DIR
type_fixes: Any = [(':\\s*STR\\b', ': str'), (':\\s*FLOAT\\b', ': float'), (':\\s*BOOL\\b', ': bool'), ('->\\s*STR\\b', '-> str'), ('->\\s*FLOAT\\b', '-> float'), ('->\\s*BOOL\\b', '-> bool')]
import_alignments: Any = []

def run_type_medic() -> Any:
    """Brief description of functionality and purpose."""
    print('[*] SOVEREIGN TYPE MEDIC: Initiating Clean Sweep...')
    modified_files: Any = 0
    # Phase 6.8: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files
    for py_file in get_python_files(CORE):
        if py_file.name == '__init__.py' or 'legacy' in str(py_file):
            continue
        try:
            with open(py_file, encoding='utf-8') as f:
                content: Any = f.read()
            original: Any = content
            for pattern, sub in TYPE_FIXES:
                content: Any = re.sub(pattern, sub, content)
            for pattern, sub in IMPORT_ALIGNMENTS:
                content: Any = re.sub(pattern, sub, content)
            if content != original:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f'  [✓] Healed: {py_file.relative_to(CORE)}')
                modified_files += 1
        except Exception as e:
            print(f'  [!] Failed to treat {py_file.name}: {e}')
    print(f'\n[OK] MEDIC COMPLETE. {modified_files} files sanitized.')
    print("    [!] NEXT: Run 'python mission_start.py' to verify the full chain.")
if __name__ == '__main__':
    run_type_medic()
