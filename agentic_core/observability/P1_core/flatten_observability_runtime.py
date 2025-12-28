import shutil
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow")
CORE = ROOT / "agentic_core"
OBS_RUNTIME = CORE / "observability/P1_core/runtime"

def flatten_observability_runtime():
    print("[*] FLATTENING observability/P1_core/runtime TO DEPTH-4...")
    moved = 0
    
    if not OBS_RUNTIME.exists():
        print("[!] Runtime directory not found")
        return
    
    # Find all Python files in subdirectories
    for py_file in OBS_RUNTIME.rglob("*.py"):
        if py_file.parent == OBS_RUNTIME:
            continue  # Already at correct depth
        
        # Create flattened name
        rel_path = py_file.relative_to(OBS_RUNTIME)
        parts = rel_path.parts[:-1]  # Exclude filename
        prefix = "_".join(parts)
        new_name = f"{prefix}_{py_file.name}"
        
        target = OBS_RUNTIME / new_name
        
        # Avoid collisions
        counter = 1
        while target.exists():
            target = OBS_RUNTIME / f"{prefix}_{counter}_{py_file.name}"
            counter += 1
        
        try:
            shutil.move(str(py_file), str(target))
            print(f"  [✓] {rel_path} -> {target.name}")
            moved += 1
        except Exception as e:
            print(f"  [X] Failed: {py_file.name} - {e}")
    
    # Clean up empty directories
    print("\n[*] Cleaning empty directories...")
    for root, dirs, files in os.walk(OBS_RUNTIME, topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            try:
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    print(f"  [✓] Removed: {dir_path.relative_to(CORE)}")
            except:
                pass
    
    print(f"\n[OK] FLATTENING COMPLETE. {moved} files moved to depth-4.")

if __name__ == "__main__":
    import os
    flatten_observability_runtime()
