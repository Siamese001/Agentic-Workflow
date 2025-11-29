#!/usr/bin/env python3
"""
Comprehensive import path fix script for engine migration.
Replaces apps.outreach_engine imports with engine paths.
"""

import os
import re
from pathlib import Path

# Comprehensive mapping dictionary (sorted by path length - longest first)
IMPORT_MAPPING = {
    # Granular subdirectory mappings (longest paths first)
    'apps.outreach_engine.l1.cms': 'engine.l1_planning.draft_planning.cms',
    'apps.outreach_engine.l1.builders': 'engine.l1_planning.draft_planning.builders',
    'apps.outreach_engine.l1.rag_planning': 'engine.l1_planning.rag_planning',
    'apps.outreach_engine.l1.safety_planning': 'engine.l1_planning.safety_planning',
    'apps.outreach_engine.l1.persona_planning': 'engine.l1_planning.safety_planning',
    'apps.outreach_engine.l1.strategy_planning': 'engine.l1_planning.strategy_planning',
    
    'apps.outreach_engine.l2.kg': 'engine.l2_execution.rag_execution.kg',
    'apps.outreach_engine.l2.vector': 'engine.l2_execution.rag_execution.vector',
    'apps.outreach_engine.l2.outreach': 'engine.l2_execution.draft_execution.outreach',
    
    'apps.outreach_engine.l3.safety': 'engine.l3_orchestration.rag_orchestration',
    
    'apps.outreach_engine.l4.entity': 'engine.l4_state.knowledge_graph',
    'apps.outreach_engine.l4.temporal_kg': 'engine.l4_state.knowledge_graph',
    'apps.outreach_engine.l4.rag': 'engine.l4_state.temporal_agents',
    'apps.outreach_engine.l4.schema': 'engine.l4_state.temporal_agents',
    
    'apps.outreach_engine.l5.guards': 'engine.l5_safety.safety_validator',
    
    # Layer-level mappings (shorter paths last)
    'apps.outreach_engine.l1': 'engine.l1_planning',
    'apps.outreach_engine.l2': 'engine.l2_execution',
    'apps.outreach_engine.l3': 'engine.l3_orchestration',
    'apps.outreach_engine.l4': 'engine.l4_state',
    'apps.outreach_engine.l5': 'engine.l5_safety',
}

def fix_imports_in_file(file_path):
    """Fix imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply replacements (longest paths first due to dictionary order)
        for old_path, new_path in IMPORT_MAPPING.items():
            # Handle "from X import Y" patterns
            content = re.sub(
                rf'from\s+{re.escape(old_path)}\s+import\s+',
                f'from {new_path} import ',
                content
            )
            # Handle "import X" patterns
            content = re.sub(
                rf'import\s+{re.escape(old_path)}(?!\w)',
                f'import {new_path}',
                content
            )
            # Handle "from X.Y import Z" where X.Y is a subpath
            content = re.sub(
                rf'from\s+{re.escape(old_path)}\.',
                f'from {new_path}.',
                content
            )
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed imports in: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def fix_all_imports(root_dir):
    """Walk through all Python files and fix imports."""
    root_path = Path(root_dir)
    fixed_count = 0
    total_count = 0
    
    for py_file in root_path.rglob("*.py"):
        # Skip __pycache__ and .git directories
        if "__pycache__" in str(py_file) or ".git" in str(py_file):
            continue
        
        total_count += 1
        if fix_imports_in_file(py_file):
            fixed_count += 1
    
    print(f"\nMigration complete!")
    print(f"Total files processed: {total_count}")
    print(f"Files with fixed imports: {fixed_count}")

if __name__ == "__main__":
    # Get the repository root directory
    script_dir = Path(__file__).parent
    repo_root = script_dir
    
    print("Starting comprehensive import path fix...")
    print(f"Repository root: {repo_root}")
    print(f"Import mappings: {len(IMPORT_MAPPING)}")
    
    fix_all_imports(repo_root)
