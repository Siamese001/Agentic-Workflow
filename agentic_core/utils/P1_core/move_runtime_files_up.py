import shutil
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow")
CORE = ROOT / "agentic_core"
OBS_RUNTIME = CORE / "observability/P1_core/runtime"
OBS_P1 = CORE / "observability/P1_core"

def move_runtime_files_up():
    print("[*] MOVING runtime files up to observability/P1_core...")
    moved = 0
    
    if not OBS_RUNTIME.exists():
        print("[!] Runtime directory not found")
        return
    
    # Move all Python files from runtime/ to P1_core/
    for py_file in OBS_RUNTIME.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        
        target = OBS_P1 / f"runtime_{py_file.name}"
        
        # Avoid collisions
        counter = 1
        while target.exists():
            target = OBS_P1 / f"runtime_{counter}_{py_file.name}"
            counter += 1
        
        try:
            shutil.move(str(py_file), str(target))
            print(f"  [✓] {py_file.name} -> {target.name}")
            moved += 1
        except Exception as e:
            print(f"  [X] Failed: {py_file.name} - {e}")
    
    # Remove empty runtime directory
    try:
        if OBS_RUNTIME.exists() and not any(OBS_RUNTIME.iterdir()):
            OBS_RUNTIME.rmdir()
            print(f"\n[✓] Removed empty directory: runtime/")
    except:
        pass
    
    print(f"\n[OK] MOVE COMPLETE. {moved} files moved to depth-4.")

if __name__ == "__main__":
    move_runtime_files_up()
