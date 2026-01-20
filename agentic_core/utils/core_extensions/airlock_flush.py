from __future__ import annotations
import os
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from pathlib import Path
from typing import Any
from agentic_core.utils.sovereign_index import SovereignIndex
from agentic_core.utils.file_utils import safe_read_file, safe_write_file
from agentic_core.utils.ssot_discovery import get_python_files

ROOT: Any = Path(__file__).parent.parent.parent.parent
CORE: Any = ROOT / 'agentic_core'

def flush_airlocks() -> Any:
    """Brief description of functionality and purpose."""
    print('[*] PERFORMING AIRLOCK FLUSH...')
    all_py = get_python_files(ROOT)
    for init_file in [f for f in all_py if f.name == '__init__.py' and str(f).startswith(str(CORE))]:
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write(f'"""Airlock: {init_file.parent.name}"""\n')
        print(f'  [✓] Flushed: {init_file.relative_to(CORE.parent)}')
if __name__ == '__main__':
    flush_airlocks()
