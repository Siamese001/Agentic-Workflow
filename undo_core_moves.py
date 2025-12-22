#!/usr/bin/env python3
"""
Undo all the incorrect core/ subdirectory moves
"""
import shutil
from pathlib import Path

def undo_core_moves():
    """Move all files back from */core/ to parent directories"""
    root = Path(".")
    
    # Directories that had files moved to core/
    directories = [
        "agentic_core",
        "apps_lic", 
        "apps_rg",
        "apps_shared",
        "config",
        "observability",
        "schemas",
        "scripts",
        "tools",
        "validator",
        "prompt_governance"
    ]
    
    moved_count = 0
    
    for dir_name in directories:
        core_path = root / dir_name / "core"
        
        if not core_path.exists():
            continue
            
        # Move all files back to parent
        for py_file in core_path.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
                
            target = core_path.parent / py_file.name
            
            if target.exists():
                print(f"Skipping {py_file} (target exists)")
                continue
                
            print(f"Moving {py_file} -> {dir_name}/{py_file.name}")
            shutil.move(str(py_file), str(target))
            moved_count += 1
        
        # Remove core directory if empty
        try:
            core_path.rmdir()
            print(f"Removed {dir_name}/core/")
        except:
            pass
    
    print(f"\nTotal files moved back: {moved_count}")

if __name__ == "__main__":
    undo_core_moves()
