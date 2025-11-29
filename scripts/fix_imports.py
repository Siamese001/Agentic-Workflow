#!/usr/bin/env python3
"""
Script to fix import statements after renaming L1->l1_planning, L2->l2_execution, L3->l3_orchestration
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix import statements in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix import paths with word boundaries to avoid false matches
        # Pattern: from agentic_core.l1_planning -> from agentic_core.l1_planning
        content = re.sub(r'\bfrom\s+agentic_core\.L1\b', 'from agentic_core.l1_planning', content)
        content = re.sub(r'\bfrom\s+agentic_core\.L2\b', 'from agentic_core.l2_execution', content)
        content = re.sub(r'\bfrom\s+agentic_core\.L3\b', 'from agentic_core.l3_orchestration', content)
        content = re.sub(r'\bfrom\s+agentic_core\.L4\b', 'from agentic_core.l4_memory_state', content)
        
        # Fix import statements
        content = re.sub(r'\bimport\s+agentic_core\.L1\b', 'import agentic_core.l1_planning', content)
        content = re.sub(r'\bimport\s+agentic_core\.L2\b', 'import agentic_core.l2_execution', content)
        content = re.sub(r'\bimport\s+agentic_core\.L3\b', 'import agentic_core.l3_orchestration', content)
        content = re.sub(r'\bimport\s+agentic_core\.L4\b', 'import agentic_core.l4_memory_state', content)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed imports in: {file_path}")
            return True
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to fix imports across the codebase"""
    root_dir = Path(__file__).parent.parent
    fixed_count = 0
    
    print("Fixing import statements after directory rename...")
    
    # Walk through all Python files
    for py_file in root_dir.rglob("*.py"):
        # Skip __pycache__ and other cache directories
        if "__pycache__" in str(py_file) or ".pytest_cache" in str(py_file):
            continue
            
        if fix_imports_in_file(py_file):
            fixed_count += 1
    
    print(f"\nCompleted! Fixed imports in {fixed_count} files.")

if __name__ == "__main__":
    main()
