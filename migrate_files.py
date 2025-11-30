#!/usr/bin/env python3
"""
File Migration Script for Agentic Workflow v10_11
Moves existing files to canonical locations with import path updates
"""

import os
import json
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

def read_file_content_safe(file_path: str) -> str:
    """Read file content safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}")
        return ""

def update_imports(content: str, old_base: str, new_base: str) -> str:
    """Update import statements to reflect new file locations"""
    # Update relative imports
    content = re.sub(
        rf'from\s+{re.escape(old_base)}\s+import',
        f'from {new_base} import',
        content
    )
    
    content = re.sub(
        rf'import\s+{re.escape(old_base)}',
        f'import {new_base}',
        content
    )
    
    return content

def migrate_agentic_core_files(base_path: Path):
    """Migrate agentic_core files to canonical locations"""
    
    # Define migration mappings based on file analysis
    migrations = [
        # Strategy Planning
        {
            "source": "agentic_core/l1_planning/planners/",
            "destinations": {
                "strategy_planner.py": "agentic_core/l1_planning/strategy_planning/blueprint/orchestration/strategy_planner.py",
                "message_planner.py": "agentic_core/l1_planning/qa_planning/question_understanding/message_planner.py",
                "research_planner.py": "agentic_core/l1_planning/qa_planning/retrieval_plans/research_planner.py",
                "refinement_planner.py": "agentic_core/l1_planning/strategy_planning/refinement/refinement_planner.py",
                "safety_planner.py": "agentic_core/l1_planning/safety_planning/policies/safety_planner.py",
            }
        },
        
        # API/Utils -> Execution Tools
        {
            "source": "agentic_core/api/",
            "destinations": {
                "models.py": "agentic_core/l2_execution/utils/models.py",
                "decorators.py": "agentic_core/l2_execution/utils/decorators.py",
                "example_engine_integration.py": "agentic_core/l2_execution/utils/example_engine_integration.py",
            }
        },
        
        # Config files -> Appropriate layers
        {
            "source": "agentic_core/config/",
            "destinations": {
                "agent_profile.py": "agentic_core/l1_planning/utils/agent_profile.py",
                "context_profile.py": "agentic_core/l1_planning/utils/context_profile.py",
                "safety_profile.py": "agentic_core/l5_safety/audit/safety_profile.py",
                "meta_profile.py": "agentic_core/l4_memory/state/meta_profile.py",
                "config_profiles_v10_10.py": "agentic_core/l3_orchestration/controllers/config_profiles_v10_10.py",
            }
        }
    ]
    
    print("=== Migrating agentic_core files ===")
    
    for migration in migrations:
        source_dir = base_path / migration["source"]
        if not source_dir.exists():
            continue
            
        print(f"\nProcessing {migration['source']}")
        
        for filename, dest_path in migration["destinations"].items():
            source_file = source_dir / filename
            dest_file = base_path / dest_path
            
            if source_file.exists():
                # Read content
                content = read_file_content_safe(str(source_file))
                if not content:
                    continue
                
                # Update imports based on destination
                old_import_base = migration["source"].rstrip('/').replace('/', '.')
                new_import_base = dest_path.rsplit('/', 1)[0].replace('/', '.')
                content = update_imports(content, old_import_base, new_import_base)
                
                # Create destination directory if needed
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Write to new location
                with open(dest_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"  Migrated: {filename} -> {dest_path}")
                
                # Remove old file after successful migration
                source_file.unlink()
                print(f"  Removed old: {migration['source']}{filename}")

def create_required_init_files(base_path: Path):
    """Create __init__.py files for all Python packages"""
    
    init_dirs = [
        # agentic_core packages
        "agentic_core/l1_planning",
        "agentic_core/l1_planning/strategy_planning",
        "agentic_core/l1_planning/strategy_planning/blueprint",
        "agentic_core/l1_planning/strategy_planning/blueprint/goals",
        "agentic_core/l1_planning/strategy_planning/blueprint/signals",
        "agentic_core/l1_planning/strategy_planning/blueprint/orchestration",
        "agentic_core/l1_planning/strategy_planning/decomposition",
        "agentic_core/l1_planning/strategy_planning/refinement",
        "agentic_core/l1_planning/qa_planning",
        "agentic_core/l1_planning/qa_planning/question_understanding",
        "agentic_core/l1_planning/qa_planning/retrieval_plans",
        "agentic_core/l1_planning/qa_planning/answer_blueprints",
        "agentic_core/l1_planning/rag_planning",
        "agentic_core/l1_planning/rag_planning/query_generation",
        "agentic_core/l1_planning/rag_planning/fusion",
        "agentic_core/l1_planning/rag_planning/routing",
        "agentic_core/l1_planning/safety_planning",
        "agentic_core/l1_planning/safety_planning/detectors",
        "agentic_core/l1_planning/safety_planning/policies",
        "agentic_core/l1_planning/safety_planning/mitigation",
        "agentic_core/l1_planning/utils",
        "agentic_core/l2_execution",
        "agentic_core/l2_execution/tools",
        "agentic_core/l2_execution/tools/browser",
        "agentic_core/l2_execution/tools/file_ops",
        "agentic_core/l2_execution/tools/api",
        "agentic_core/l2_execution/execution_engines",
        "agentic_core/l2_execution/utils",
        "agentic_core/l3_orchestration",
        "agentic_core/l3_orchestration/dag",
        "agentic_core/l3_orchestration/dag/node_types",
        "agentic_core/l3_orchestration/react",
        "agentic_core/l3_orchestration/controllers",
        "agentic_core/l4_memory",
        "agentic_core/l4_memory/short_term",
        "agentic_core/l4_memory/long_term",
        "agentic_core/l4_memory/state",
        "agentic_core/l5_safety",
        "agentic_core/l5_safety/filters",
        "agentic_core/l5_safety/guardrails",
        "agentic_core/l5_safety/audit",
    ]
    
    print("\n=== Creating __init__.py files ===")
    
    for dir_path in init_dirs:
        full_path = base_path / dir_path
        if full_path.exists():
            init_file = full_path / "__init__.py"
            if not init_file.exists():
                with open(init_file, 'w', encoding='utf-8') as f:
                    f.write('"""Package initialization."""\n')
                print(f"  Created: {dir_path}/__init__.py")

def cleanup_old_directories(base_path: Path):
    """Remove empty old directories after migration"""
    
    old_dirs_to_check = [
        "agentic_core/api",
        "agentic_core/config",
        "agentic_core/l1_planning/planners"
    ]
    
    print("\n=== Cleaning up old directories ===")
    
    for dir_path in old_dirs_to_check:
        full_path = base_path / dir_path
        if full_path.exists() and not any(full_path.iterdir()):
            full_path.rmdir()
            print(f"  Removed empty directory: {dir_path}")

def run_migration():
    """Execute the complete migration process"""
    base_path = Path(__file__).parent
    
    print("=== Starting File Migration ===")
    
    # Run migration steps
    migrate_agentic_core_files(base_path)
    create_required_init_files(base_path)
    cleanup_old_directories(base_path)
    
    print("\n=== Migration complete ===")
    print("Next steps:")
    print("1. Run import smoke test: python -c 'import agentic_core'")
    print("2. Run pytest: pytest -q")
    print("3. Run ruff: ruff check .")

if __name__ == "__main__":
    run_migration()
