#!/usr/bin/env python3
"""
Find empty directories in the project.
"""

import os

def find_empty_directories():
    """Find all empty directories excluding cache and hidden directories."""
    empty_dirs = []
    
    for root, dirs, files in os.walk("."):
        if root.startswith("./.") or root.startswith("./runtime/cache"):
            continue
        
        # Check if directory is empty (no subdirectories and no files)
        if not dirs and not files and root != ".":
            empty_dirs.append(root)
    
    return empty_dirs

if __name__ == "__main__":
    empty_dirs = find_empty_directories()
    
    print(f"Found {len(empty_dirs)} empty directories:")
    for dir_path in empty_dirs:
        print(f"  {dir_path}")
    
    if empty_dirs:
        print(f"\nCreating .gitkeep files in empty directories...")
        for dir_path in empty_dirs:
            gitkeep_path = os.path.join(dir_path, ".gitkeep")
            with open(gitkeep_path, 'w') as f:
                f.write("# This file ensures the directory is tracked by git\n")
            print(f"  Created: {gitkeep_path}")
    else:
        print("No empty directories found!")
