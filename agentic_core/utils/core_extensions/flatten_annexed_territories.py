"""
Flatten annexed territories to SSOT-compliant depth.
[SSOT] All depth requirements derived from SOVEREIGN_REGISTRY in structure_blueprint.py
"""
import os
import shutil
from pathlib import Path

from agentic_core.config.blueprint_sovereign.structure_blueprint import SOVEREIGN_REGISTRY

ROOT = Path("C:/Git/Agentic-Workflow")
CORE = ROOT / "agentic_core"

# [SSOT] Get required depth for agentic_core from SOVEREIGN_REGISTRY
REQUIRED_DEPTH = SOVEREIGN_REGISTRY["agentic_core"]["depth"]

# Layers that were just annexed and need flattening
ANNEXED_LAYERS = ["config", "observability", "prompt_governance", "schemas"]

def flatten_annexed():
    print(f"[*] FLATTENING ANNEXED TERRITORIES TO DEPTH-{REQUIRED_DEPTH}...")
    moved = 0
    
    for layer in ANNEXED_LAYERS:
        layer_path = CORE / layer
        if not layer_path.exists():
            continue
            
        print(f"\n[*] Processing layer: {layer}")
        
        # Find all P1_core subdirectories
        for stage_dir in layer_path.iterdir():
            if not stage_dir.is_dir() or stage_dir.name == "__pycache__":
                continue
                
            # [SSOT] Look for nested subdirectories exceeding required depth
            for subdir in stage_dir.rglob("*"):
                if subdir.is_file() and subdir.suffix == ".py":
                    # Calculate current depth
                    rel_path = subdir.relative_to(CORE)
                    parts = rel_path.parts
                    
                    # [SSOT] If depth > required (Layer/Stage/File), move to Stage level
                    if len(parts) > REQUIRED_DEPTH - 1:
                        # Move to Layer/Stage/filename
                        target = CORE / parts[0] / parts[1] / subdir.name
                        
                        # Avoid collisions
                        if target.exists():
                            # Add parent dir name as prefix
                            target = CORE / parts[0] / parts[1] / f"{parts[2]}_{subdir.name}"
                        
                        try:
                            shutil.move(str(subdir), str(target))
                            print(f"  [✓] Flattened: {rel_path} -> {target.relative_to(CORE)}")
                            moved += 1
                        except Exception as e:
                            print(f"  [X] Failed: {subdir.name} - {e}")
    
    # Clean up empty directories
    print("\n[*] Cleaning empty directories...")
    for layer in ANNEXED_LAYERS:
        layer_path = CORE / layer
        if not layer_path.exists():
            continue
            
        for root, dirs, files in os.walk(layer_path, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    if not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        print(f"  [✓] Removed empty: {dir_path.relative_to(CORE)}")
                except:
                    pass
    
    print(f"\n[OK] FLATTENING COMPLETE. {moved} files moved to depth-{REQUIRED_DEPTH}.")

if __name__ == "__main__":
    flatten_annexed()
