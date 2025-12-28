"""
Fix depth violations by moving shallow files into proper stage subdirectories.
Files at Layer/file.py need to move to Layer/Stage/file.py
"""
import shutil
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow")
CORE = ROOT / "agentic_core"

# Define stage mappings for each layer
STAGE_MAPPINGS = {
    "L1_cognition": "P1_core",
    "L2_execution": "P1_core", 
    "L3_orchestration": "P1_core",
    "L4_state": "P1_core",
    "L5_safety": "P1_core",
    "memory": "P1_core",
    "patterns": "P1_core",
    "runtime": "P1_core",
    "utils": "P1_core",
}

def fix_depth_violations():
    """Move shallow files into proper stage subdirectories."""
    print("[*] FIXING DEPTH VIOLATIONS...")
    moved = 0
    
    for layer_name, default_stage in STAGE_MAPPINGS.items():
        layer_path = CORE / layer_name
        if not layer_path.exists():
            continue
        
        # Find files directly in layer (depth 3)
        for py_file in layer_path.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            # Determine target stage
            stage_path = layer_path / default_stage
            stage_path.mkdir(exist_ok=True)
            
            # Create stage __init__.py if it doesn't exist
            stage_init = stage_path / "__init__.py"
            if not stage_init.exists():
                stage_init.write_text('"""Stage module."""\n')
            
            # Move file
            target = stage_path / py_file.name
            if not target.exists():
                shutil.move(str(py_file), str(target))
                print(f"  [✓] Moved: {py_file.relative_to(CORE)} -> {target.relative_to(CORE)}")
                moved += 1
            else:
                print(f"  [SKIP] Already exists: {target.relative_to(CORE)}")
    
    print(f"\n[OK] Moved {moved} files to proper depth")
    return moved

if __name__ == "__main__":
    fix_depth_violations()
    print("\n[!] NEXT: Run 'python sovereign_lock.py' to verify compliance")
