#!/usr/bin/env python3
"""
Script to find and fix empty directories in the repository
Section 3 compliance: No folder or subfolder at Levels 0–3 may be empty
"""

import os
from pathlib import Path

def find_empty_directories(root_path):
    """Find all empty directories excluding cache and venv folders"""
    empty_dirs = []
    
    for root, dirs, files in os.walk(root_path):
        # Skip cache, venv, and __pycache__ directories
        dirs[:] = [d for d in dirs if not any(skip in d.lower() for skip in ['cache', 'venv', '__pycache__'])]
        
        # Skip if we're in a cache/venv directory
        if any(skip in root.lower() for skip in ['cache', 'venv', '__pycache__']):
            continue
            
        # Check if directory is empty (no files and no subdirectories)
        if not files and not dirs:
            empty_dirs.append(root)
    
    return empty_dirs

def fix_empty_directory(dir_path):
    """Add appropriate placeholder file to empty directory"""
    dir_path = Path(dir_path)
    
    # Determine if this is a Python package directory
    if any(parent.name in ['agentic_core', 'apps', 'prompt_governance', 'tests'] for parent in dir_path.parents):
        # Create __init__.py for Python packages
        init_file = dir_path / '__init__.py'
        if not init_file.exists():
            init_file.write_text('# Placeholder file for Section 3 compliance\n')
            return f'Created __init__.py in {dir_path}'
    else:
        # Create .gitkeep for non-Python directories
        gitkeep_file = dir_path / '.gitkeep'
        if not gitkeep_file.exists():
            gitkeep_file.write_text('# Placeholder file for Section 3 compliance\n')
            return f'Created .gitkeep in {dir_path}'
    
    return f'Directory already has placeholder file: {dir_path}'

def main():
    """Main function to find and fix empty directories"""
    repo_root = Path(__file__).parent
    
    # Focus on main repository directories (Level 1)
    main_dirs = [
        'agentic_core',
        'apps', 
        'prompt_governance',
        'tests',
        'schemas',
        'observability',
        'runtime'
    ]
    
    print("🔍 Scanning for empty directories...")
    
    all_empty_dirs = []
    for main_dir in main_dirs:
        main_path = repo_root / main_dir
        if main_path.exists():
            empty_dirs = find_empty_directories(main_path)
            all_empty_dirs.extend(empty_dirs)
            print(f"Found {len(empty_dirs)} empty directories in {main_dir}/")
    
    print(f"\n📊 Total empty directories found: {len(all_empty_dirs)}")
    
    if all_empty_dirs:
        print("\n🔧 Fixing empty directories...")
        for empty_dir in all_empty_dirs:
            result = fix_empty_directory(empty_dir)
            print(f"  ✅ {result}")
        
        print(f"\n✅ Fixed {len(all_empty_dirs)} empty directories for Section 3 compliance!")
    else:
        print("\n✅ No empty directories found - Section 3 compliance maintained!")

if __name__ == "__main__":
    main()
