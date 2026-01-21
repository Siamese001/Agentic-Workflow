from __future__ import annotations

import os

'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import shutil
from pathlib import Path
from typing import Any

root: Any = Path('C:/Git/Agentic-Workflow/agentic_core')

def collapse_tunnels() -> Any:
    """Brief description of functionality and purpose."""
    print('[*] COLLAPSING DIRECTORY TUNNELS...')
    for root, dirs, _files in os.walk(ROOT, topdown=False):
        for name in dirs:
            parent_path: Any = Path(root) / name
            child_path: Any = parent_path / name
            if child_path.exists() and child_path.is_dir():
                print(f'  [!] Found Tunnel: {parent_path.name}/{child_path.name}')
                for item in child_path.iterdir():
                    shutil.move(str(item), str(parent_path / item.name))
                child_path.rmdir()
                print('  [✓] Tunnel Collapsed.')
if __name__ == '__main__':
    collapse_tunnels()
