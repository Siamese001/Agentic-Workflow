#!/usr/bin/env python3
"""
Targeted Migration: Convert Specific Hyphenated Folders to Underscores

This script converts ONLY the 22 specific hyphenated folders created during
the general folder elimination to underscored names for Python import compatibility,
while keeping the YAML SSoT with hyphenated names as canonical labels.

Usage:
    python targeted_underscore_migration.py [--dry-run] [--execute]
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent

# The exact 22 hyphenated folders from general folder elimination
HYPHENATED_FOLDERS = [
    # L1_cognition
    "01_agentic_core/L1_cognition/P1_retrieve/gather-context-inputs",
    "01_agentic_core/L1_cognition/P1_retrieve/gather-context-inputs/integrate-source-signals", 
    "01_agentic_core/L1_cognition/P2_inspect/detect-anomalies",
    "01_agentic_core/L1_cognition/P2_inspect/detect-anomalies/analyze-symptoms",
    "01_agentic_core/L1_cognition/P3_aggregate/execute-actions",
    "01_agentic_core/L1_cognition/P3_aggregate/execute-actions/invoke-functions",
    "01_agentic_core/L1_cognition/P3_aggregate/select-optimal",
    "01_agentic_core/L1_cognition/P3_aggregate/select-optimal/evaluate-options",
    "01_agentic_core/L1_cognition/P3_aggregate/sync-status",
    "01_agentic_core/L1_cognition/P3_aggregate/sync-status/update-memory",
    "01_agentic_core/L1_cognition/P4_safety/control-resources",
    "01_agentic_core/L1_cognition/P4_safety/control-resources/track-usage",
    
    # L2_execution
    "01_agentic_core/L2_execution/P3_aggregate/execute-actions",
    "01_agentic_core/L2_execution/P3_aggregate/execute-actions/invoke-functions",
    
    # L3_orchestration
    "01_agentic_core/L3_orchestration/P1_retrieve/gather-context-inputs",
    "01_agentic_core/L3_orchestration/P1_retrieve/gather-context-inputs/integrate-source-signals",
    "01_agentic_core/L3_orchestration/P3_aggregate/execute-actions", 
    "01_agentic_core/L3_orchestration/P3_aggregate/execute-actions/invoke-functions",
    
    # L4_memory
    "01_agentic_core/L4_memory/P1_retrieve/gather-context-inputs",
    "01_agentic_core/L4_memory/P1_retrieve/gather-context-inputs/integrate-source-signals",
    
    # L5_safety
    "01_agentic_core/L5_safety/P4_safety/control-resources",
    "01_agentic_core/L5_safety/P4_safety/control-resources/track-usage"
]

def validate_folders_exist(folders: List[str]) -> List[str]:
    """Validate that all target folders exist."""
    missing = []
    for folder_path in folders:
        full_path = PROJECT_ROOT / folder_path
        if not full_path.exists():
            missing.append(folder_path)
    return missing

def generate_rename_plan(folders: List[str]) -> List[Tuple[Path, str]]:
    """Generate rename plan converting hyphens to underscores, sorted by depth (deepest first)."""
    rename_plan = []
    
    for folder_path in folders:
        full_path = PROJECT_ROOT / folder_path
        new_name = full_path.name.replace('-', '_')
        new_path = full_path.parent / new_name
        rename_plan.append((full_path, str(new_path), len(folder_path.split('/'))))
    
    # Sort by depth (deepest first) to avoid path invalidation
    rename_plan.sort(key=lambda x: x[2], reverse=True)
    
    # Remove depth from return tuple
    return [(item[0], item[1]) for item in rename_plan]

def validate_rename_plan(rename_plan: List[Tuple[Path, str]]) -> List[str]:
    """Check for conflicts in rename plan."""
    errors = []
    target_paths = set()
    
    for old_path, new_path_str in rename_plan:
        new_path = Path(new_path_str)
        
        if new_path.exists():
            errors.append(f"Target already exists: {new_path}")
        
        if new_path in target_paths:
            errors.append(f"Duplicate target: {new_path}")
        target_paths.add(new_path)
        
        if not new_path.name.isidentifier():
            errors.append(f"Invalid Python identifier: {new_path.name}")
    
    return errors

def execute_rename_plan(rename_plan: List[Tuple[Path, str]], dry_run: bool = False) -> bool:
    """Execute the rename plan using git mv."""
    if dry_run:
        logger.info("DRY RUN - The following renames would be performed:")
        for old_path, new_path in rename_plan:
            logger.info(f"  {old_path} -> {new_path}")
        return True
    
    logger.info(f"Executing {len(rename_plan)} folder renames...")
    
    for old_path, new_path_str in rename_plan:
        new_path = Path(new_path_str)
        
        try:
            # Two-step git mv for Windows
            temp_name = f"{old_path.name}_temp"
            temp_path = old_path.parent / temp_name
            
            logger.info(f"Renaming: {old_path} -> {new_path}")
            
            # Step 1
            result = subprocess.run([
                'git', 'mv', str(old_path), str(temp_path)
            ], capture_output=True, text=True, cwd=PROJECT_ROOT)
            
            if result.returncode != 0:
                logger.error(f"Failed to move {old_path} to temp: {result.stderr}")
                return False
            
            # Step 2
            result = subprocess.run([
                'git', 'mv', str(temp_path), str(new_path)
            ], capture_output=True, text=True, cwd=PROJECT_ROOT)
            
            if result.returncode != 0:
                logger.error(f"Failed to move temp to {new_path}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error renaming {old_path}: {e}")
            return False
    
    return True

def update_phase01_translation() -> bool:
    """Add bidirectional translation functions to phase01.py."""
    phase01_path = PROJECT_ROOT / 'phase01' / 'phase01.py'
    
    with open(phase01_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'def translate_to_python(' in content:
        logger.info("Translation functions already exist")
        return True
    
    new_functions = '''
    def translate_to_python(name: str) -> str:
        """Convert filesystem path (underscores) to Python identifier (underscores)"""
        return name

    def translate_to_yaml(name: str) -> str:
        """Convert filesystem path (underscores) to YAML canonical name (hyphens)"""
        return name.replace('_', '-')
'''
    
    insert_pos = content.find('def translate_to_filesystem(')
    if insert_pos == -1:
        logger.error("translate_to_filesystem function not found")
        return False
    
    func_end = content.find('\n\n', insert_pos)
    if func_end == -1:
        func_end = len(content)
    
    updated_content = content[:func_end] + new_functions + content[func_end:]
    
    with open(phase01_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    logger.info("Added bidirectional translation functions")
    return True

def main():
    parser = argparse.ArgumentParser(description='Targeted hyphenated folder migration')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed')
    parser.add_argument('--execute', action='store_true', help='Perform the migration')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        parser.print_help()
        return 1
    
    logger.info("Starting targeted hyphenated folder migration...")
    logger.info(f"Project root: {PROJECT_ROOT}")
    
    # Validate folders exist
    missing = validate_folders_exist(HYPHENATED_FOLDERS)
    if missing:
        logger.error("Missing folders:")
        for folder in missing:
            logger.error(f"  - {folder}")
        return 1
    
    # Generate rename plan
    rename_plan = generate_rename_plan(HYPHENATED_FOLDERS)
    
    # Validate plan
    errors = validate_rename_plan(rename_plan)
    if errors:
        logger.error("Validation errors:")
        for error in errors:
            logger.error(f"  - {error}")
        return 1
    
    logger.info(f"Migration plan: {len(rename_plan)} folders")
    
    if args.dry_run:
        execute_rename_plan(rename_plan, dry_run=True)
        logger.info("DRY RUN completed. Use --execute to perform migration.")
        return 0
    
    # Update phase01.py
    if not update_phase01_translation():
        logger.error("Failed to update phase01.py")
        return 1
    
    # Execute migration
    if not execute_rename_plan(rename_plan, dry_run=False):
        logger.error("Migration failed")
        return 1
    
    logger.info("Migration completed successfully!")
    logger.info("Next steps:")
    logger.info("1. Review with 'git status'")
    logger.info("2. Test Python imports")
    logger.info("3. Commit changes")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
