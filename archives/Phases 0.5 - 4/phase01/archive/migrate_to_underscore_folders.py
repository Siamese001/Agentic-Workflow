#!/usr/bin/env python3
"""
Migration Script: Convert Hyphenated Folders to Underscores

This script converts all hyphenated filesystem folders to underscored names
to ensure Python import compatibility, while keeping the YAML SSoT with
hyphenated names as the canonical labels.

Usage:
    python migrate_to_underscore_folders.py [--dry-run] [--execute]
    
    --dry-run: Show what would be changed without executing
    --execute: Perform the actual migration (requires git operations)
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict, Set
import argparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Project configuration
PROJECT_ROOT = Path(__file__).parent.parent
TARGET_DOMAINS = [
    '01_agentic_core',
    '02_schemas', 
    '03_runtime',
    '04_prompt_governance',
    '05_config',
    '06_data',
    '07_observability',
    '08_scripts',
    '09_apps',
    '10_tests'
]

# Skip legacy/backup folders
SKIP_PATTERNS = [
    'phase1_legacy_folders',
    'phase1_backup',
    '_unassigned_duplicates'
]

def find_hyphenated_folders(root: Path) -> List[Path]:
    """Find all folders with hyphens in their names within target domains."""
    hyphenated_folders = []
    
    for domain in TARGET_DOMAINS:
        domain_path = root / domain
        if not domain_path.exists():
            logger.warning(f"Domain path does not exist: {domain_path}")
            continue
            
        # Skip if domain itself is in a backup location
        if any(skip in str(domain_path) for skip in SKIP_PATTERNS):
            logger.info(f"Skipping backup domain: {domain_path}")
            continue
            
        # Find all hyphenated folders recursively
        for folder in domain_path.rglob('*'):
            if folder.is_dir() and '-' in folder.name:
                # Skip backup/legacy folders
                if any(skip in str(folder) for skip in SKIP_PATTERNS):
                    continue
                    
                hyphenated_folders.append(folder)
    
    return sorted(hyphenated_folders)

def generate_rename_plan(folders: List[Path]) -> List[Tuple[Path, str]]:
    """Generate a plan for renaming folders from hyphens to underscores."""
    rename_plan = []
    
    for folder in folders:
        new_name = folder.name.replace('-', '_')
        new_path = folder.parent / new_name
        rename_plan.append((folder, str(new_path)))
    
    return rename_plan

def validate_rename_plan(rename_plan: List[Tuple[Path, str]]) -> List[str]:
    """Validate that the rename plan won't cause conflicts."""
    errors = []
    target_paths = set()
    
    for old_path, new_path_str in rename_plan:
        new_path = Path(new_path_str)
        
        # Check if target already exists
        if new_path.exists():
            errors.append(f"Target already exists: {new_path}")
        
        # Check for duplicate targets
        if new_path in target_paths:
            errors.append(f"Duplicate target path: {new_path}")
        target_paths.add(new_path)
        
        # Check if rename would create invalid Python identifiers
        if not new_path.name.isidentifier():
            errors.append(f"Invalid Python identifier: {new_path.name}")
    
    return errors

def execute_rename_plan(rename_plan: List[Tuple[Path, str]], dry_run: bool = False) -> bool:
    """Execute the rename plan using git mv for proper tracking."""
    if dry_run:
        logger.info("DRY RUN - The following renames would be performed:")
        for old_path, new_path in rename_plan:
            logger.info(f"  {old_path} -> {new_path}")
        return True
    
    logger.info(f"Executing {len(rename_plan)} folder renames...")
    
    for old_path, new_path_str in rename_plan:
        new_path = Path(new_path_str)
        
        try:
            # Use two-step git mv for Windows case-insensitive filesystem
            temp_name = f"{old_path.name}_temp_rename"
            temp_path = old_path.parent / temp_name
            
            logger.info(f"Renaming: {old_path} -> {new_path}")
            
            # Step 1: Move to temporary name
            result = subprocess.run([
                'git', 'mv', str(old_path), str(temp_path)
            ], capture_output=True, text=True, cwd=PROJECT_ROOT)
            
            if result.returncode != 0:
                logger.error(f"Failed to move {old_path} to temp: {result.stderr}")
                return False
            
            # Step 2: Move to final name
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
    """Update phase01.py to include bidirectional translation functions."""
    phase01_path = PROJECT_ROOT / 'phase01' / 'phase01.py'
    
    if not phase01_path.exists():
        logger.error(f"phase01.py not found at {phase01_path}")
        return False
    
    # Read current content
    with open(phase01_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if bidirectional functions already exist
    if 'def translate_to_python(' in content:
        logger.info("Bidirectional translation functions already exist in phase01.py")
        return True
    
    # Add bidirectional translation functions after translate_to_filesystem
    new_functions = '''
    def translate_to_python(name: str) -> str:
        """Convert filesystem path (underscores) to Python identifier (underscores)"""
        # For now, filesystem and Python use the same convention (underscores)
        return name

    def translate_to_yaml(name: str) -> str:
        """Convert filesystem path (underscores) to YAML canonical name (hyphens)"""
        return name.replace('_', '-')
'''
    
    # Find insertion point after translate_to_filesystem function
    insert_pos = content.find('def translate_to_filesystem(')
    if insert_pos == -1:
        logger.error("translate_to_filesystem function not found in phase01.py")
        return False
    
    # Find end of translate_to_filesystem function
    func_end = content.find('\n\n', insert_pos)
    if func_end == -1:
        func_end = len(content)
    
    # Insert new functions
    updated_content = content[:func_end] + new_functions + content[func_end:]
    
    # Write updated content
    with open(phase01_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    logger.info("Added bidirectional translation functions to phase01.py")
    return True

def generate_summary_report(rename_plan: List[Tuple[Path, str]]) -> Dict:
    """Generate a summary report of the migration."""
    summary = {
        'total_folders': len(rename_plan),
        'domains_affected': set(),
        'folder_types': {},
        'examples': []
    }
    
    for old_path, new_path in rename_plan:
        # Track affected domains
        domain = old_path.parts[0] if len(old_path.parts) > 0 else 'unknown'
        summary['domains_affected'].add(domain)
        
        # Track folder types (by depth)
        depth = len(old_path.parts)
        summary['folder_types'][depth] = summary['folder_types'].get(depth, 0) + 1
        
        # Add examples (first 5)
        if len(summary['examples']) < 5:
            summary['examples'].append({
                'old': str(old_path),
                'new': new_path
            })
    
    summary['domains_affected'] = sorted(list(summary['domains_affected']))
    
    return summary

def main():
    parser = argparse.ArgumentParser(description='Migrate hyphenated folders to underscores')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed')
    parser.add_argument('--execute', action='store_true', help='Perform the actual migration')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        parser.print_help()
        return 1
    
    logger.info("Starting hyphenated folder migration...")
    logger.info(f"Project root: {PROJECT_ROOT}")
    
    # Find all hyphenated folders
    hyphenated_folders = find_hyphenated_folders(PROJECT_ROOT)
    logger.info(f"Found {len(hyphenated_folders)} hyphenated folders")
    
    if not hyphenated_folders:
        logger.info("No hyphenated folders found. Migration complete.")
        return 0
    
    # Generate rename plan
    rename_plan = generate_rename_plan(hyphenated_folders)
    
    # Validate rename plan
    errors = validate_rename_plan(rename_plan)
    if errors:
        logger.error("Validation errors found:")
        for error in errors:
            logger.error(f"  - {error}")
        return 1
    
    # Generate summary report
    summary = generate_summary_report(rename_plan)
    logger.info("Migration Summary:")
    logger.info(f"  Total folders to rename: {summary['total_folders']}")
    logger.info(f"  Domains affected: {', '.join(summary['domains_affected'])}")
    logger.info(f"  Examples:")
    for example in summary['examples']:
        logger.info(f"    {example['old']} -> {example['new']}")
    
    if args.dry_run:
        logger.info("DRY RUN completed. Use --execute to perform the migration.")
        return 0
    
    # Confirm execution
    if not args.execute:
        logger.info("Use --execute to perform the actual migration.")
        return 0
    
    # Update phase01.py translation functions
    if not update_phase01_translation():
        logger.error("Failed to update phase01.py translation functions")
        return 1
    
    # Execute rename plan
    if not execute_rename_plan(rename_plan, dry_run=False):
        logger.error("Migration failed during rename execution")
        return 1
    
    logger.info("Migration completed successfully!")
    logger.info("Next steps:")
    logger.info("1. Review the changes with 'git status'")
    logger.info("2. Test Python imports to ensure they work")
    logger.info("3. Commit the changes with an appropriate commit message")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
