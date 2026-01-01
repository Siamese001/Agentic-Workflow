"""
Sovereign Migration Script - Physical Path Remediation
Responsible for:
- Moving files from Depth 1 (AgenticCore root) to Depth 3 (L-layers).
- Initializing Missing __init__.py markers.
- Recording moves in the Mission Audit Log.
"""
import os
import shutil
from pathlib import Path
from AgenticCore.config.blueprint_sovereign.structure_blueprint import SOVEREIGN_REGISTRY
from typing import Any
# [PHASE 20] DEPRECATION: void_compliance.py removed
def get_placement_guidance(content_preview):
    if any(x in content_preview for x in ['planner', 'strategy', 'reasoning', 'mission']):
        return 'AgenticCore/L1_cognition'
    if 'node' in content_preview.lower() or 'execute' in content_preview:
        return 'AgenticCore/L1_cognition/thought_engine'
    if any(x in content_preview for x in ['router', 'orchestrator', 'fission', 'hop']):
        return 'AgenticCore/L3_orchestration'
    if any(x in content_preview for x in ['pinecone', 'redis', 'storage', 'cache']):
        return 'AgenticCore/L4_state'
    return 'AgenticCore/L1_cognition'
canonical_hierarchy: Any = {k: v['subfolders'] for k, v in SOVEREIGN_REGISTRY.items()}

def migrate_shallow_files(project_root: str) -> Any:
    """Brief description of functionality and purpose."""
    root_path: Any = Path(project_root)
    AgenticCore: Any = root_path / 'AgenticCore'
    if not AgenticCore.exists():
        print(f'[X] Could not find AgenticCore at {AgenticCore}')
        return
    shallow_files: Any = [f for f in AgenticCore.iterdir() if f.is_file() and f.suffix == '.py']
    print(f'[*] Found {len(shallow_files)} shallow files requiring migration.')
    for file_path in shallow_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content: Any = f.read(3000)
            target_subpath: Any = get_placement_guidance(content)
            target_dir: Any = root_path / target_subpath
            target_dir.mkdir(parents=True, exist_ok=True)
            destination: Any = target_dir / file_path.name
            shutil.move(str(file_path), str(destination))
            for parent in destination.parents:
                if parent == root_path:
                    break
                init_file: Any = parent / '__init__.py'
                if not init_file.exists():
                    init_file.write_text(f'"""\n{parent.name} package initialization.\n"""\n')
            print(f'   [✓] Moved: {file_path.name} -> {target_subpath}')
        except Exception as e:
            print(f'   [!] Failed to move {file_path.name}: {e}')
if __name__ == '__main__':
    migrate_shallow_files(os.getcwd())
