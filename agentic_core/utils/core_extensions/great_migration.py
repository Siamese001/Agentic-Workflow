"""
Sovereign Migration Script - Physical Path Remediation
Responsible for:
- Moving files from Depth 1 (agentic_core root) to Depth 3 (L-layers).
- Initializing missing __init__.py markers.
- Recording moves in the Mission Audit Log.
"""
import os
import shutil
from pathlib import Path
from agentic_core.config.blueprint_sovereign.structure_blueprint import SOVEREIGN_REGISTRY
from agentic_core.runtime.shared.void_compliance import get_placement_guidance
canonical_hierarchy: Any = {k: v['subfolders'] for k, v in SOVEREIGN_REGISTRY.items()}

def migrate_shallow_files(project_root: str) -> Any:
    """Brief description of functionality and purpose."""
    root_path: Any = Path(project_root)
    agentic_core: Any = root_path / 'agentic_core'
    if not agentic_core.exists():
        print(f'[X] Could not find agentic_core at {agentic_core}')
        return
    shallow_files: Any = [f for f in agentic_core.iterdir() if f.is_file() and f.suffix == '.py']
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
