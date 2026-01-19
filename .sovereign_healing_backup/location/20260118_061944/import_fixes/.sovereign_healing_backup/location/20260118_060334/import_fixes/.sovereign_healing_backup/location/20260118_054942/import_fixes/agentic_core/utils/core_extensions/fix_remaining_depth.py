from __future__ import annotations
"""Move remaining shallow files to proper depth."""
import shutil
from pathlib import Path

# [SSOT IMPORT] Structure blueprint is the single source of truth
from typing import Any
from agentic_core.L5_safety.validators.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

root: Any = Path('C:/Git/Agentic-Workflow')
core: Any = ROOT / 'agentic_core'

def move_remaining() -> Any:
    """Move remaining depth 3 files to P1_core."""
    print('[*] MOVING REMAINING SHALLOW FILES...')
    moved: Any = 0
    knowledge_dir: Any = CORE / 'knowledge'
    if knowledge_dir.exists():
        stage: Any = knowledge_dir / 'P1_core'
        stage.mkdir(exist_ok=True)
        (stage / '__init__.py').write_text('"""Stage module."""\n')
        for f in knowledge_dir.glob('*.py'):
            if f.name != '__init__.py':
                target: Any = stage / f.name
                if not target.exists():
                    shutil.move(str(f), str(target))
                    print(f'  [✓] Moved: {f.relative_to(CORE)}')
                    moved += 1
    thought_nodes: Any = CORE / 'L1_cognition' / 'thought_engine'
    if thought_nodes.exists():
        stage: Any = thought_nodes / 'P1_core'
        stage.mkdir(exist_ok=True)
        (stage / '__init__.py').write_text('"""Stage module."""\n')
        for f in thought_nodes.glob('*.py'):
            if f.name != '__init__.py':
                target: Any = stage / f.name
                if not target.exists():
                    shutil.move(str(f), str(target))
                    print(f'  [✓] Moved: {f.relative_to(CORE)}')
                    moved += 1
    print(f'\n[OK] Moved {moved} files')
if __name__ == '__main__':
    move_remaining()
