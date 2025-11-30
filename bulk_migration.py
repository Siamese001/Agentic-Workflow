#!/usr/bin/env python3
"""
Bulk Migration Script for Agentic Workflow v10_11
Moves entire directories and files to canonical locations
"""

import os
import shutil
from pathlib import Path

def bulk_migrate_agentic_core(base_path: Path):
    """Bulk migrate agentic_core directories to canonical structure"""
    
    print("=== Bulk Migrating agentic_core ===")
    
    # Directory mappings (old -> new)
    directory_moves = [
        # L2 Execution: executors -> execution_engines
        ("agentic_core/l2_execution/executors", "agentic_core/l2_execution/execution_engines"),
        
        # L3 Orchestration: engines/framework -> specific canonical dirs
        ("agentic_core/l3_orchestration/engines", "agentic_core/l3_orchestration/dag"),
        ("agentic_core/l3_orchestration/framework", "agentic_core/l3_orchestration/controllers"),
    ]
    
    # File mappings for standalone files
    file_moves = [
        # Move strategy_planning.py to appropriate location
        ("agentic_core/l1_planning/strategy_planning.py", "agentic_core/l1_planning/strategy_planning/blueprint/orchestration/strategy_planning.py"),
        ("agentic_core/l2_execution/l2_execution.py", "agentic_core/l2_execution/execution_engines/l2_execution.py"),
        ("agentic_core/l3_orchestration/l3_orchestration.py", "agentic_core/l3_orchestration/dag/l3_orchestration.py"),
    ]
    
    # Execute directory moves
    for old_dir, new_dir in directory_moves:
        old_path = base_path / old_dir
        new_path = base_path / new_dir
        
        if old_path.exists() and old_path.is_dir():
            if new_path.exists():
                # Merge directories if destination exists
                print(f"  Merging {old_dir} -> {new_dir}")
                for item in old_path.iterdir():
                    dest_item = new_path / item.name
                    if item.is_file() and not dest_item.exists():
                        shutil.move(str(item), str(dest_item))
                    elif item.is_dir() and not dest_item.exists():
                        shutil.move(str(item), str(dest_item))
            else:
                # Move entire directory
                print(f"  Moving {old_dir} -> {new_dir}")
                shutil.move(str(old_path), str(new_path))
            
            # Remove old directory if empty
            if old_path.exists() and not any(old_path.iterdir()):
                old_path.rmdir()
                print(f"  Removed empty: {old_dir}")
    
    # Execute file moves
    for old_file, new_file in file_moves:
        old_path = base_path / old_file
        new_path = base_path / new_file
        
        if old_path.exists():
            print(f"  Moving {old_file} -> {new_file}")
            new_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(old_path), str(new_path))

def move_engines_to_apps(base_path: Path):
    """Move outreach_engine and resume_engine from agentic_core to apps"""
    
    print("\n=== Moving engines to apps/ ===")
    
    engine_moves = [
        ("agentic_core/outreach_engine", "apps/outreach_engine"),
        ("agentic_core/resume_engine", "apps/resume_engine"),
    ]
    
    for old_dir, new_dir in engine_moves:
        old_path = base_path / old_dir
        new_path = base_path / new_dir
        
        if old_path.exists():
            print(f"  Moving {old_dir} -> {new_dir}")
            if new_path.exists():
                # Merge with existing canonical structure
                for item in old_path.iterdir():
                    dest_item = new_path / item.name
                    if item.is_file() and not dest_item.exists():
                        shutil.move(str(item), str(dest_item))
                    elif item.is_dir():
                        # Recursively merge subdirectories
                        for sub_item in item.iterdir():
                            sub_dest = dest_item / sub_item.name
                            if not sub_dest.exists():
                                shutil.move(str(sub_item), str(sub_dest))
            else:
                shutil.move(str(old_path), str(new_path))
            
            # Remove old directory if empty
            if old_path.exists() and not any(old_path.iterdir()):
                old_path.rmdir()

def cleanup_agentic_core_extras(base_path: Path):
    """Remove extra directories that don't belong in agentic_core"""
    
    print("\n=== Cleaning up agentic_core extras ===")
    
    dirs_to_remove = [
        "agentic_core/models",  # Should go to schemas/
        "agentic_core/runtime", # Should be separate root
    ]
    
    for dir_path in dirs_to_remove:
        full_path = base_path / dir_path
        if full_path.exists():
            print(f"  Removing: {dir_path}")
            shutil.rmtree(str(full_path))

def create_all_init_files(base_path: Path):
    """Create __init__.py files for all packages"""
    
    print("\n=== Creating __init__.py files ===")
    
    # Walk through all directories and create __init__.py where needed
    for root_dir in ["agentic_core", "apps", "config"]:
        root_path = base_path / root_dir
        if not root_path.exists():
            continue
            
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Skip __pycache__ and other cache dirs
            dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
            
            init_file = Path(dirpath) / "__init__.py"
            if not init_file.exists():
                with open(init_file, 'w', encoding='utf-8') as f:
                    f.write('"""Package initialization."""\n')

def run_bulk_migration():
    """Execute the complete bulk migration"""
    base_path = Path(__file__).parent
    
    print("=== Starting Bulk Migration ===")
    
    # Execute migration steps
    bulk_migrate_agentic_core(base_path)
    move_engines_to_apps(base_path)
    cleanup_agentic_core_extras(base_path)
    create_all_init_files(base_path)
    
    print("\n=== Bulk migration complete ===")
    print("Next steps:")
    print("1. Run import smoke test: python -c 'import agentic_core'")
    print("2. Run structure diff analysis: python structure_diff_analyzer.py")

if __name__ == "__main__":
    run_bulk_migration()
