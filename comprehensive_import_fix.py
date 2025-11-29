#!/usr/bin/env python3
"""
Comprehensive Import Fix Script for L1-L3 Reorganization
Windsurf Rules.md Section 3 Compliance - Phase 3

This script fixes all import paths affected by the L1-L3 structural reorganization:
- L1: draft_planning/rag_planning → planners/, cms/ → schemas/, builders/ → utils/
- L2: draft_execution/rag_execution → engines/, removed bullet_execution/subatomic
- L3: agent_orchestration/rag_orchestration → framework/, draft_orchestration → engines.resume/
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

def get_import_mappings() -> Dict[str, str]:
    """Return comprehensive mapping of old import paths to new paths."""
    return {
        # L1 Planning mappings
        "agentic_core.l1_planning.draft_planning": "agentic_core.l1_planning.planners",
        "agentic_core.l1_planning.rag_planning": "agentic_core.l1_planning.planners", 
        "agentic_core.l1_planning.safety_planning": "agentic_core.l1_planning.planners",
        "agentic_core.l1_planning.strategy_planning": "agentic_core.l1_planning.planners",
        "agentic_core.l1_planning.cms": "agentic_core.l1_planning.schemas",
        "agentic_core.l1_planning.builders": "agentic_core.l1_planning.utils",
        
        # L2 Execution mappings  
        "agentic_core.l2_execution.draft_execution": "agentic_core.l2_execution.engines",
        "agentic_core.l2_execution.rag_execution": "agentic_core.l2_execution.engines",
        "agentic_core.l2_execution.bullet_execution": "agentic_core.l2_execution.engines",
        "agentic_core.l2_execution.subatomic": "agentic_core.l2_execution.engines",
        
        # L3 Orchestration mappings
        "agentic_core.l3_orchestration.agent_orchestration": "agentic_core.l3_orchestration.framework",
        "agentic_core.l3_orchestration.rag_orchestration": "agentic_core.l3_orchestration.framework", 
        "agentic_core.l3_orchestration.draft_orchestration": "agentic_core.l3_orchestration.engines.resume",
        
        # Specific file mappings for conflicts
        "lic_prompt_builder": "prompt_builder",
        "builders.prompt_builder": "utils.prompt_builder",
    }

def get_relative_import_mappings() -> Dict[str, str]:
    """Return mappings for relative imports within agentic_core."""
    return {
        # L1 relative imports
        r"\.draft_planning\.": ".planners.",
        r"\.rag_planning\.": ".planners.",
        r"\.safety_planning\.": ".planners.",
        r"\.strategy_planning\.": ".planners.",
        r"\.cms\.": ".schemas.",
        r"\.builders\.": ".utils.",
        
        # L2 relative imports
        r"\.draft_execution\.": ".engines.",
        r"\.rag_execution\.": ".engines.",
        r"\.bullet_execution\.": ".engines.",
        r"\.subatomic\.": ".engines.",
        
        # L3 relative imports
        r"\.agent_orchestration\.": ".framework.",
        r"\.rag_orchestration\.": ".framework.",
        r"\.draft_orchestration\.": ".engines.resume.",
    }

def fix_imports_in_file(file_path: Path, mappings: Dict[str, str], relative_mappings: Dict[str, str]) -> bool:
    """Fix imports in a single Python file. Returns True if changes were made."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix absolute imports
        for old_path, new_path in mappings.items():
            # Handle "from old_path import" patterns
            content = re.sub(
                rf"from\s+{re.escape(old_path)}\s+import",
                f"from {new_path} import",
                content
            )
            # Handle "import old_path" patterns  
            content = re.sub(
                rf"import\s+{re.escape(old_path)}",
                f"import {new_path}",
                content
            )
        
        # Fix relative imports
        for old_pattern, new_pattern in relative_mappings.items():
            content = re.sub(old_pattern, new_pattern, content)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def find_python_files(root_dir: Path) -> List[Path]:
    """Find all Python files in the repository."""
    python_files = []
    for file_path in root_dir.rglob("*.py"):
        # Skip __pycache__ and other cache directories
        if "__pycache__" not in str(file_path):
            python_files.append(file_path)
    return python_files

def main():
    """Main function to fix all imports."""
    root_dir = Path(__file__).parent
    mappings = get_import_mappings()
    relative_mappings = get_relative_import_mappings()
    
    print("🔧 Comprehensive Import Fix - L1-L3 Reorganization")
    print("=" * 60)
    
    # Find all Python files
    python_files = find_python_files(root_dir)
    print(f"📁 Found {len(python_files)} Python files")
    
    # Fix imports in each file
    changed_files = 0
    for file_path in python_files:
        if fix_imports_in_file(file_path, mappings, relative_mappings):
            changed_files += 1
            print(f"✅ Fixed: {file_path.relative_to(root_dir)}")
    
    print("=" * 60)
    print(f"🎯 Complete: {changed_files}/{len(python_files)} files updated")
    print("🧹 Next step: Clean __pycache__ directories and validate")
    
    # Clean __pycache__ directories
    print("\n🧹 Cleaning __pycache__ directories...")
    for pycache_dir in root_dir.rglob("__pycache__"):
        try:
            import shutil
            shutil.rmtree(pycache_dir)
            print(f"🗑️  Removed: {pycache_dir.relative_to(root_dir)}")
        except Exception as e:
            print(f"⚠️  Could not remove {pycache_dir}: {e}")

if __name__ == "__main__":
    main()
