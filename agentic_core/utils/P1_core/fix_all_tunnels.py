import os
import shutil
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow")
CORE = ROOT / "agentic_core"

def fix_tunnel_violations():
    """Moves files from deep tunnels up to proper depth-4 structure."""
    print("[*] FIXING ALL TUNNEL VIOLATIONS...")
    fixed = 0
    
    for py_file in CORE.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        
        parts = py_file.relative_to(CORE).parts
        
        # If depth > 3 (which means total depth > 4), we have a tunnel
        if len(parts) > 3:
            # Target structure: Layer/Stage/file.py
            layer = parts[0]  # e.g., L1_cognition
            stage = parts[1]  # e.g., P1_core
            
            # Everything else is the tunnel - flatten it
            # Take the filename from the deepest level
            filename = py_file.name
            
            # Target location: Layer/Stage/filename
            target_dir = CORE / layer / stage
            target_file = target_dir / filename
            
            # If target already exists, prepend the subdirectory name to avoid collision
            if target_file.exists():
                # Use the immediate parent folder name as prefix
                prefix = parts[2]  # First subdirectory after stage
                target_file = target_dir / f"{prefix}_{filename}"
            
            try:
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(py_file), str(target_file))
                print(f"  [✓] Flattened: {py_file.relative_to(CORE)} -> {target_file.relative_to(CORE)}")
                fixed += 1
            except Exception as e:
                print(f"  [!] Failed to move {py_file.name}: {e}")
    
    print(f"\n[OK] TUNNEL FIX COMPLETE. {fixed} files moved to proper depth.")
    
    # Clean up empty directories
    print("\n[*] CLEANING UP EMPTY DIRECTORIES...")
    cleaned = 0
    for root, dirs, files in os.walk(CORE, topdown=False):
        for name in dirs:
            dir_path = Path(root) / name
            try:
                # Only remove if empty (no files, no subdirs)
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    print(f"  [✓] Removed empty: {dir_path.relative_to(CORE)}")
                    cleaned += 1
            except:
                pass
    
    print(f"\n[OK] CLEANUP COMPLETE. {cleaned} empty directories removed.")

if __name__ == "__main__":
    fix_tunnel_violations()
