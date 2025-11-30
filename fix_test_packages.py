#!/usr/bin/env python3
"""
Remove __init__.py files from test directories to prevent pytest package issues
"""

import os
from pathlib import Path

def remove_test_init_files(base_path: Path):
    """Remove __init__.py files from test directories"""
    
    print("=== Removing Test Package __init__.py Files ===")
    
    # Find all __init__.py files in test directories
    test_init_files = []
    
    # Search in tests/ directory
    tests_dir = base_path / "tests"
    if tests_dir.exists():
        test_init_files.extend(tests_dir.rglob("__init__.py"))
    
    # Search in apps/*/tests/ directories  
    apps_dir = base_path / "apps"
    if apps_dir.exists():
        for app_dir in apps_dir.iterdir():
            if app_dir.is_dir():
                app_tests_dir = app_dir / "tests"
                if app_tests_dir.exists():
                    test_init_files.extend(app_tests_dir.rglob("__init__.py"))
    
    # Remove the __init__.py files
    removed_count = 0
    for init_file in test_init_files:
        if init_file.exists():
            print(f"  Removing: {init_file.relative_to(base_path)}")
            init_file.unlink()
            removed_count += 1
    
    print(f"\n=== Removed {removed_count} __init__.py files ===")
    print("Test directories are no longer Python packages")
    print("Next steps:")
    print("1. Run pytest with PYTHONPATH: pytest -q")
    print("2. Check if import errors are resolved")

def run_fix():
    """Execute the fix"""
    base_path = Path(__file__).parent
    remove_test_init_files(base_path)

if __name__ == "__main__":
    run_fix()
