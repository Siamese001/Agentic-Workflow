import os
import shutil
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow")
CORE = ROOT / "agentic_core"

# Layers that were just annexed and need flattening
ANNEXED_LAYERS = ["config", "observability", "prompt_governance", "schemas"]

def flatten_annexed():
    print("[*] FLATTENING ANNEXED TERRITORIES TO DEPTH-4...")
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
                
            # Look for nested subdirectories (depth 5+)
            for subdir in stage_dir.rglob("*"):
                if subdir.is_file() and subdir.suffix == ".py":
                    # Calculate current depth
                    rel_path = subdir.relative_to(CORE)
                    parts = rel_path.parts
                    
                    # If depth > 3 (Layer/Stage/File), move to Stage level
                    if len(parts) > 3:
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
    
    print(f"\n[OK] FLATTENING COMPLETE. {moved} files moved to depth-4.")

if __name__ == "__main__":
    flatten_annexed()
