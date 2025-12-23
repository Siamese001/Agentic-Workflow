import os
import shutil
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow")
CORE = ROOT / "agentic_core"
SCRIPTS_DIR = CORE / "L0_maintenance/scripts"

def flatten_scripts():
    print("[*] FLATTENING L0_maintenance/scripts TO DEPTH-4...")
    moved = 0
    
    if not SCRIPTS_DIR.exists():
        print("[!] Scripts directory not found")
        return
    
    # Find all Python files at depth > 4
    for py_file in SCRIPTS_DIR.rglob("*.py"):
        rel_path = py_file.relative_to(CORE)
        parts = rel_path.parts
        
        # If depth > 3 (Layer/Stage/File), move to Stage level
        if len(parts) > 3:
            # Create a flattened name from the path
            # e.g., 03_runtime/shared/openai_client.py -> 03_runtime_shared_openai_client.py
            path_prefix = "_".join(parts[2:-1])  # Skip Layer/Stage and filename
            new_name = f"{path_prefix}_{py_file.name}"
            
            target = SCRIPTS_DIR / new_name
            
            # Avoid collisions
            counter = 1
            while target.exists():
                target = SCRIPTS_DIR / f"{path_prefix}_{counter}_{py_file.name}"
                counter += 1
            
            try:
                shutil.move(str(py_file), str(target))
                print(f"  [✓] {rel_path} -> {target.relative_to(CORE)}")
                moved += 1
            except Exception as e:
                print(f"  [X] Failed: {py_file.name} - {e}")
    
    # Clean up empty directories
    print("\n[*] Cleaning empty directories...")
    for root, dirs, files in os.walk(SCRIPTS_DIR, topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            try:
                if not any(dir_path.iterdir()) and dir_path != SCRIPTS_DIR:
                    dir_path.rmdir()
                    print(f"  [✓] Removed: {dir_path.relative_to(CORE)}")
            except:
                pass
    
    print(f"\n[OK] FLATTENING COMPLETE. {moved} files moved to depth-4.")

if __name__ == "__main__":
    flatten_scripts()
