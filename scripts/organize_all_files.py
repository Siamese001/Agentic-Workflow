#!/usr/bin/env python3
"""
Comprehensive file organization script for sovereign silos
Moves ALL file types from root to appropriate directories
"""

import argparse
import logging
import os
import shutil

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def organize_all_files():
    """Move ALL files from root to appropriate sovereign silos"""
    logger.info("📁 Starting comprehensive file organization...")
    
    # Files that MUST stay in root
    essential_files = {
        'Dockerfile', 'docker-compose.yml', 'requirements.txt', 
        '.gitignore', '.env', '.env.example', '.env.production',
        '.env.production.template', 'pyproject.toml'
    }
    
    # File type mappings to directories
    file_mappings = {
        # Configuration files
        'config': ['.yml', '.yaml', '.json', '.toml', '.ini', '.env*'],
        
        # Documentation
        'docs': ['.md', '.txt', '.rst'],
        
        # Scripts
        'scripts': ['.sh', '.ps1', '.bat'],
        
        # Docker files
        'docker': ['.dockerignore', 'Dockerfile.*'],
        
        # Backup files
        'archives': ['.backup', '.old', '.bak'],
        
        # Special files
        'data': ['.csv', '.jsonl', '.parquet', '.db', '.sqlite'],
        
        # Python files (already handled but include for completeness)
        'agentic_core': ['action_node.py', 'agent_logic.py', 'cognitive_node.py'],
        'apps_rg': ['orchestrator.py', 'llm_client.py'],
        'apps_shared': ['db_manager.py', 'etl_pipeline.py'],
        'tests': ['test_*.py', '*_test.py'],
        'scripts': ['fix_*.py', 'clean_*.py', 'assess_*.py']
    }
    
    moved_count = 0
    created_dirs = set()
    
    # Get all files in root
    root_files = [f for f in os.listdir('.') if os.path.isfile(f)]
    
    for filename in root_files:
        # Skip essential files
        if filename in essential_files:
            logger.info(f"⏭️  Keeping essential file: {filename}")
            continue
            
        # Skip hidden files that should stay in root
        if filename.startswith('.') and filename not in ['.dockerignore.backup', '.dockerignore.old']:
            logger.info(f"⏭️  Keeping hidden file: {filename}")
            continue
            
        # Determine target directory
        target_dir = None
        
        # Check exact filename matches first
        for directory, patterns in file_mappings.items():
            for pattern in patterns:
                if '*' in pattern:
                    # Handle wildcards
                    if pattern.replace('*', '') in filename:
                        target_dir = directory
                        break
                elif pattern.endswith('*'):
                    # Handle prefix matches
                    if filename.startswith(pattern[:-1]):
                        target_dir = directory
                        break
                elif pattern.startswith('*'):
                    # Handle suffix matches
                    if filename.endswith(pattern[1:]):
                        target_dir = directory
                        break
                elif pattern == filename:
                    # Exact match
                    target_dir = directory
                    break
            if target_dir:
                break
        
        # If no match, check file extension
        if not target_dir:
            ext = os.path.splitext(filename)[1]
            if ext:
                for directory, patterns in file_mappings.items():
                    if ext in patterns:
                        target_dir = directory
                        break
        
        # Default to scripts for unknown file types
        if not target_dir:
            target_dir = 'scripts'
        
        # Create directory if it doesn't exist
        if target_dir not in created_dirs:
            os.makedirs(target_dir, exist_ok=True)
            created_dirs.add(target_dir)
            logger.info(f"📁 Created directory: {target_dir}")
        
        # Move the file
        try:
            dst_path = os.path.join(target_dir, filename)
            if not os.path.exists(dst_path):
                shutil.move(filename, dst_path)
                logger.info(f"📁 Moved {filename} -> {target_dir}/")
                moved_count += 1
            else:
                logger.warning(f"⚠️  File already exists: {dst_path}")
        except Exception as e:
            logger.error(f"❌ Failed to move {filename}: {e}")
    
    logger.info(f"\n✨ Organization complete!")
    logger.info(f"📁 Moved {moved_count} files")
    logger.info(f"📂 Created {len(created_dirs)} new directories")
    
    return moved_count

def show_remaining_files():
    """Show what files are left in root"""
    logger.info("\n📋 Files remaining in root:")
    root_files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for f in sorted(root_files):
        logger.info(f"  - {f}")
    logger.info(f"\nTotal: {len(root_files)} files")

def main():
    parser = argparse.ArgumentParser(description="Organize all files into sovereign silos")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be moved without actually moving")
    parser.add_argument("--show-remaining", action="store_true", help="Show files left in root")
    args = parser.parse_args()
    
    if args.show_remaining:
        show_remaining_files()
    elif args.dry_run:
        logger.info("🔍 DRY RUN - No files will be moved")
        # TODO: Implement dry run logic
    else:
        organize_all_files()
        show_remaining_files()

if __name__ == "__main__":
    main()
