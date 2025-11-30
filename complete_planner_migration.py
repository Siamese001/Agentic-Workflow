#!/usr/bin/env python3
"""
Complete Planner Migration to Canonical Structure
Moves all remaining planner files to appropriate canonical locations
"""

import os
import shutil
from pathlib import Path

def migrate_planners_to_canonical(base_path: Path):
    """Migrate all planner files to their canonical locations"""
    
    print("=== Migrating Planners to Canonical Structure ===")
    
    # Define canonical mappings for planner files
    planner_mappings = [
        # Strategy Planning
        {
            "source": "agentic_core/l1_planning/planners/strategy_planner.py",
            "dest": "agentic_core/l1_planning/strategy_planning/blueprint/orchestration/strategy_planner.py"
        },
        
        # QA Planning
        {
            "source": "agentic_core/l1_planning/planners/message_planner.py", 
            "dest": "agentic_core/l1_planning/qa_planning/question_understanding/message_planner.py"
        },
        {
            "source": "agentic_core/l1_planning/planners/research_planner.py",
            "dest": "agentic_core/l1_planning/qa_planning/retrieval_plans/research_planner.py"
        },
        
        # Strategy Planning - Refinement
        {
            "source": "agentic_core/l1_planning/planners/refinement_planner.py",
            "dest": "agentic_core/l1_planning/strategy_planning/refinement/refinement_planner.py"
        },
        
        # Safety Planning
        {
            "source": "agentic_core/l1_planning/planners/safety_planner.py",
            "dest": "agentic_core/l1_planning/safety_planning/policies/safety_planner.py"
        }
    ]
    
    # Execute migrations
    for mapping in planner_mappings:
        source_file = base_path / mapping["source"]
        dest_file = base_path / mapping["dest"]
        
        if source_file.exists():
            print(f"  Moving {mapping['source']} -> {mapping['dest']}")
            
            # Create destination directory if needed
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file
            shutil.move(str(source_file), str(dest_file))
        else:
            print(f"  Warning: Source not found {mapping['source']}")
    
    # Remove empty planners directory
    planners_dir = base_path / "agentic_core/l1_planning/planners"
    if planners_dir.exists() and not any(planners_dir.iterdir()):
        planners_dir.rmdir()
        print("  Removed empty planners directory")

def update_test_imports_for_planners(base_path: Path):
    """Update test imports to use new canonical planner locations"""
    
    print("\n=== Updating Test Imports for Planners ===")
    
    # Define import replacements for planner imports
    replacements = [
        # Strategy planner
        (r'from agentic_core\.l1_planning\.planners\.strategy_planner import', 
         'from agentic_core.l1_planning.strategy_planning.blueprint.orchestration.strategy_planner import'),
        
        # Message planner  
        (r'from agentic_core\.l1_planning\.planners\.message_planner import',
         'from agentic_core.l1_planning.qa_planning.question_understanding.message_planner import'),
        
        # Research planner
        (r'from agentic_core\.l1_planning\.planners\.research_planner import',
         'from agentic_core.l1_planning.qa_planning.retrieval_plans.research_planner import'),
        
        # Refinement planner
        (r'from agentic_core\.l1_planning\.planners\.refinement_planner import',
         'from agentic_core.l1_planning.strategy_planning.refinement.refinement_planner import'),
        
        # Safety planner
        (r'from agentic_core\.l1_planning\.planners\.safety_planner import',
         'from agentic_core.l1_planning.safety_planning.policies.safety_planner import'),
    ]
    
    # Find and update test files
    tests_dir = base_path / "tests"
    test_files = list(tests_dir.rglob("test_*.py"))
    
    files_updated = 0
    total_updates = 0
    
    for test_file in test_files:
        if not test_file.exists():
            continue
            
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Warning: Could not read {test_file}: {e}")
            continue
        
        original_content = content
        updates_in_file = 0
        
        # Apply replacements
        for old_pattern, new_pattern in replacements:
            new_content = content.replace(old_pattern, new_pattern)
            if new_content != content:
                updates_in_file += 1
                content = new_content
        
        # Write back if changed
        if content != original_content:
            try:
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                files_updated += 1
                total_updates += updates_in_file
                print(f"  Updated {updates_in_file} imports in {test_file.name}")
            except Exception as e:
                print(f"Warning: Could not write to {test_file}: {e}")
    
    print(f"\n=== Test Import Update Summary ===")
    print(f"Files updated: {files_updated}")
    print(f"Total import updates: {total_updates}")

def run_complete_planner_migration():
    """Execute the complete planner migration"""
    base_path = Path(__file__).parent
    
    print("=== Starting Complete Planner Migration ===")
    
    # Run migration steps
    migrate_planners_to_canonical(base_path)
    update_test_imports_for_planners(base_path)
    
    print("\n=== Complete planner migration finished ===")
    print("Next steps:")
    print("1. Test a specific planner: pytest tests/l1_planning/unit/test_rg_strategy_planner.py -v")
    print("2. Run all tests: pytest -q")

if __name__ == "__main__":
    run_complete_planner_migration()
