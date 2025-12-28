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

from agentic_core.config.P1_core.structure_blueprint import SOVEREIGN_REGISTRY
from agentic_core.runtime.shared.void_compliance import get_placement_guidance

CANONICAL_HIERARCHY = {k: v["subfolders"] for k, v in SOVEREIGN_REGISTRY.items()}

def migrate_shallow_files(project_root: str):
    root_path = Path(project_root)
    agentic_core = root_path / "agentic_core"
    
    if not agentic_core.exists():
        print(f"[X] Could not find agentic_core at {agentic_core}")
        return

    # Find all Python files directly in the root of agentic_core (Depth 1)
    shallow_files = [f for f in agentic_core.iterdir() if f.is_file() and f.suffix == ".py"]
    print(f"[*] Found {len(shallow_files)} shallow files requiring migration.")

    for file_path in shallow_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read(3000)
            
            # Use SSOT heuristics to determine the new home
            target_subpath = get_placement_guidance(content)
            target_dir = root_path / target_subpath
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Execute physical move
            destination = target_dir / file_path.name
            shutil.move(str(file_path), str(destination))
            
            # Ensure __init__.py markers exist for package integrity
            for parent in destination.parents:
                if parent == root_path: break
                init_file = parent / "__init__.py"
                if not init_file.exists():
                    init_file.write_text(f'"""\n{parent.name} package initialization.\n"""\n')
            
            print(f"   [✓] Moved: {file_path.name} -> {target_subpath}")
            
        except Exception as e:
            print(f"   [!] Failed to move {file_path.name}: {e}")

if __name__ == "__main__":
    migrate_shallow_files(os.getcwd())
