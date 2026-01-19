from __future__ import annotations
"""
Purge illegal __init__.py airlocks using SSOT depth requirements.
[SSOT] All depth requirements derived from SOVEREIGN_REGISTRY in structure_blueprint.py
"""
import os
from pathlib import Path
from agentic_core.config.blueprint_sovereign.structure_blueprint import SOVEREIGN_REGISTRY
from typing import Any
root_dir: Any = Path('C:/Git/Agentic-Workflow/agentic_core')
required_depth: Any = SOVEREIGN_REGISTRY['agentic_core']['depth']

def purge_illegal_airlocks() -> Any:
    """Brief description of functionality and purpose."""
    print(f'[*] SOVEREIGN DEEP-CLEAN: Purging Illegal Airlocks (SSOT depth: {REQUIRED_DEPTH})...')
    deleted_count: Any = 0
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            if file == '__init__.py':
                full_path: Any = Path(root) / file
                rel_path: Any = full_path.relative_to(ROOT_DIR)
                parts: Any = rel_path.parts
                depth: Any = len(parts)
                if depth > REQUIRED_DEPTH - 1 or (depth == 1 and rel_path.name == '__init__.py'):
                    try:
                        os.remove(full_path)
                        print(f'  [X] Purged: {rel_path}')
                        deleted_count += 1
                    except Exception as e:
                        print(f'  [!] Failed to delete {rel_path}: {e}')
    print(f'\n[OK] DEEP-CLEAN COMPLETE. {deleted_count} illegal airlocks removed.')
if __name__ == '__main__':
    purge_illegal_airlocks()
