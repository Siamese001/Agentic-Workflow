#!/usr/bin/env python3
"""
Repository Cache Purge Utility

Recursively deletes all Python cache artifacts and temporary files
to ensure clean repository state across branches and commits.
"""

import os
import shutil
from pathlib import Path

def purge_repository_cache(target_path=None):
    """Recursively deletes artifacts, skipping large ignored directories."""
    root_dir = Path(target_path) if target_path else Path(__file__).parent.parent
    # SSOT: Ignore massive or unauthorized root folders
    ignore_dirs = {".git", ".venv", "venv", "env", "data", "archives"}
    
    removed_count = 0
    error_count = 0

    print(f"Purging artifacts in {root_dir}...")

    for root, dirs, files in os.walk(root_dir):
        # Prune ignored directories in-place for sub-second performance
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        current_path = Path(root)
        
        for d in list(dirs):
            if d in ("__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".sovereign_healing_backup") or d.startswith("temp_"):
                dir_path = current_path / d
                try:
                    shutil.rmtree(dir_path)
                    print(f"Removed directory: {dir_path.relative_to(root_dir)}")
                    removed_count += 1
                    dirs.remove(d) 
                except Exception as e:
                    print(f"WARNING: Could not remove {dir_path}: {e}")
                    error_count += 1

        for f in files:
            if f.endswith((".pyc", ".pyo")):
                file_path = current_path / f
                try:
                    file_path.unlink()
                    print(f"Removed file: {file_path.relative_to(root_dir)}")
                    removed_count += 1
                except Exception as e:
                    print(f"WARNING: Could not remove {file_path}: {e}")
                    error_count += 1
                
    print(f"Cleanup complete: {removed_count} items removed, {error_count} errors")
    return removed_count, error_count

if __name__ == "__main__":
    purge_repository_cache()
