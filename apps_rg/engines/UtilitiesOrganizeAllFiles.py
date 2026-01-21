from __future__ import annotations

"""
Comprehensive file organization script for sovereign silos
Moves ALL file types from root to appropriate directories
"""
import argparse
import logging
import os
import shutil
from typing import Any

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
)

logging.basicConfig(level=logging.INFO, format='%(message)s')
Logger: Any = logging.getLogger(__name__)

def organize_all_files() -> Any:
    """Move ALL files from root to appropriate sovereign silos"""
    Logger.info('📁 Starting comprehensive file organization...')
    essential_files: Any = {'Dockerfile', 'docker-compose.yml', 'requirements.txt', '.gitignore', '.env', '.env.example', '.env.production', '.env.production.template', 'pyproject.toml'}
    file_mappings: Any = {'config': ['.yml', '.yaml', '.json', '.toml', '.ini', '.env*'], 'docs': ['.md', '.txt', '.rst'], SCRIPTS_DIR: ['.sh', '.ps1', '.bat'], 'docker': ['.dockerignore', 'Dockerfile.*'], ARCHIVES_DIR: ['.backup', '.old', '.bak'], 'data': ['.csv', '.jsonl', '.parquet', '.db', '.sqlite'], AGENTIC_CORE_DIR: ['ActionNode.py', 'agent_logic.py', 'CognitiveNode.py'], APPS_RG_DIR: ['orchestrator.py', 'llm_client.py'], APPS_SHARED_DIR: ['db_manager.py', 'etl_pipeline.py'], TESTS_DIR: ['test_*.py', '*_test.py'], SCRIPTS_DIR: ['fix_*.py', 'clean_*.py', 'assess_*.py']}
    moved_count: Any = 0
    created_dirs: Any = set()
    root_files: Any = [f for f in os.listdir('.') if os.path.isfile(f)]
    for filename in root_files:
        if filename in essential_files:
            Logger.info(f'⏭️  Keeping essential file: {filename}')
            continue
        if filename.startswith('.') and filename not in ['.dockerignore.backup', '.dockerignore.old']:
            Logger.info(f'⏭️  Keeping hidden file: {filename}')
            continue
        target_dir: Any = None
        for directory, patterns in file_mappings.items():
            for pattern in patterns:
                if '*' in pattern:
                    if pattern.replace('*', '') in filename:
                        target_dir: Any = directory
                        break
                elif pattern.endswith('*'):
                    if filename.startswith(pattern[:-1]):
                        target_dir: Any = directory
                        break
                elif pattern.startswith('*'):
                    if filename.endswith(pattern[1:]):
                        target_dir: Any = directory
                        break
                elif pattern == filename:
                    target_dir: Any = directory
                    break
            if target_dir:
                break
        if not target_dir:
            ext: Any = os.path.splitext(filename)[1]
            if ext:
                for directory, patterns in file_mappings.items():
                    if ext in patterns:
                        target_dir: Any = directory
                        break
        if not target_dir:
            target_dir: Any = SCRIPTS_DIR
        if target_dir not in created_dirs:
            os.makedirs(target_dir, exist_ok=True)
            created_dirs.add(target_dir)
            Logger.info(f'📁 Created directory: {target_dir}')
        try:
            dst_path: Any = os.path.join(target_dir, filename)
            if not os.path.exists(dst_path):
                shutil.move(filename, dst_path)
                Logger.info(f'📁 Moved {filename} -> {target_dir}/')
                moved_count += 1
            else:
                Logger.warning(f'⚠️  File already exists: {dst_path}')
        except Exception as e:
            Logger.error(f'❌ Failed to move {filename}: {e}')
    Logger.info('\n✨ Organization complete!')
    Logger.info(f'📁 Moved {moved_count} files')
    Logger.info(f'📂 Created {len(created_dirs)} new directories')
    return moved_count

def show_remaining_files() -> Any:
    """Show what files are left in root"""
    Logger.info('\n📋 Files remaining in root:')
    root_files: Any = [f for f in os.listdir('.') if os.path.isfile(f)]
    for f in sorted(root_files):
        Logger.info(f'  - {f}')
    Logger.info(f'\nTotal: {len(root_files)} files')

def main() -> Any:
    """Brief description of functionality and purpose."""
    parser: Any = argparse.ArgumentParser(description='Organize all files into sovereign silos')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be moved without actually moving')
    parser.add_argument('--show-remaining', action='store_true', help='Show files left in root')
    args: Any = parser.parse_args()
    if args.show_remaining:
        show_remaining_files()
    elif args.dry_run:
        Logger.info('🔍 DRY RUN - No files will be moved')
    else:
        organize_all_files()
        show_remaining_files()
if __name__ == '__main__':
    main()
