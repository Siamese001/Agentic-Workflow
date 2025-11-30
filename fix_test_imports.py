#!/usr/bin/env python3
"""
Fix Test Import Paths for Agentic Workflow v10_11
Updates all broken imports in test files after bulk migration
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path: Path, replacements: list) -> int:
    """Fix imports in a single file, return number of changes made"""
    if not file_path.exists():
        return 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}")
        return 0
    
    original_content = content
    changes_made = 0
    
    # Apply all replacement patterns
    for old_pattern, new_pattern in replacements:
        new_content = re.sub(old_pattern, new_pattern, content)
        if new_content != content:
            changes_made += 1
            content = new_content
    
    # Write back if changes were made
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  Fixed {changes_made} imports in: {file_path.name}")
        except Exception as e:
            print(f"Warning: Could not write to {file_path}: {e}")
            return 0
    
    return changes_made

def fix_all_test_imports(base_path: Path):
    """Fix imports in all test files"""
    
    print("=== Fixing Test Import Paths ===")
    
    # Define import replacement patterns
    replacements = [
        # Framework -> Controllers
        (r'from agentic_core\.l3_orchestration\.framework\.', 'from agentic_core.l3_orchestration.controllers.'),
        (r'import agentic_core\.l3_orchestration\.framework\.', 'import agentic_core.l3_orchestration.controllers.'),
        
        # Engines -> DAG
        (r'from agentic_core\.l3_orchestration\.engines\.', 'from agentic_core.l3_orchestration.dag.'),
        (r'import agentic_core\.l3_orchestration\.engines\.', 'import agentic_core.l3_orchestration.dag.'),
        
        # Resume engine moved to apps
        (r'from agentic_core\.resume_engine\.', 'from apps.resume_engine.'),
        (r'import agentic_core\.resume_engine\.', 'import apps.resume_engine.'),
        
        # Outreach engine moved to apps  
        (r'from agentic_core\.outreach_engine\.', 'from apps.outreach_engine.'),
        (r'import agentic_core\.outreach_engine\.', 'import apps.outreach_engine.'),
        
        # Fix specific engine module references
        (r'resume_engine_dag', 'dag'),
        (r'outreach_engine_dag', 'dag'),
        (r'dag_executor', 'dag'),
        (r'self_correction', 'controllers'),
    ]
    
    # Find all Python test files
    test_files = []
    tests_dir = base_path / "tests"
    apps_tests_dir = base_path / "apps" / "resume_engine" / "tests"
    outreach_tests_dir = base_path / "apps" / "outreach_engine" / "tests"
    
    for search_dir in [tests_dir, apps_tests_dir, outreach_tests_dir]:
        if search_dir.exists():
            for py_file in search_dir.rglob("*.py"):
                if py_file.name.startswith("test_"):
                    test_files.append(py_file)
    
    print(f"Found {len(test_files)} test files to process")
    
    total_changes = 0
    files_changed = 0
    
    for test_file in test_files:
        changes = fix_imports_in_file(test_file, replacements)
        if changes > 0:
            total_changes += changes
            files_changed += 1
    
    print(f"\n=== Import Fix Summary ===")
    print(f"Files processed: {len(test_files)}")
    print(f"Files changed: {files_changed}")
    print(f"Total import fixes: {total_changes}")

def fix_agentic_core_init_imports(base_path: Path):
    """Fix imports in agentic_core layer __init__.py files"""
    
    print("\n=== Fixing agentic_core __init__.py imports ===")
    
    # Fix l3_orchestration __init__.py
    l3_init = base_path / "agentic_core" / "l3_orchestration" / "__init__.py"
    if l3_init.exists():
        with open(l3_init, 'r') as f:
            content = f.read()
        
        # Remove broken import
        content = re.sub(r'from \.l3_orchestration import.*\n', '', content)
        
        with open(l3_init, 'w') as f:
            f.write(content)
        print("  Fixed agentic_core/l3_orchestration/__init__.py")
    
    # Fix l5_safety __init__.py
    l5_init = base_path / "agentic_core" / "l5_safety" / "__init__.py"
    if l5_init.exists():
        with open(l5_init, 'r') as f:
            content = f.read()
        
        # Remove broken imports
        content = re.sub(r'from agentic_core\.resume_engine\.l5_safety\.policies import.*\n', '', content)
        content = re.sub(r'from agentic_core\.outreach_engine\.l5_safety\.policies import.*\n', '', content)
        
        with open(l5_init, 'w') as f:
            f.write(content)
        print("  Fixed agentic_core/l5_safety/__init__.py")

def run_import_fixes():
    """Execute all import fixes"""
    base_path = Path(__file__).parent
    
    print("=== Starting Test Import Fixes ===")
    
    # Run all fix steps
    fix_all_test_imports(base_path)
    fix_agentic_core_init_imports(base_path)
    
    print("\n=== Import fixes complete ===")
    print("Next steps:")
    print("1. Run pytest: pytest -q")
    print("2. Run ruff: ruff check .")

if __name__ == "__main__":
    run_import_fixes()
