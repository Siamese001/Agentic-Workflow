from __future__ import annotations
"""
Enhanced cleanup script that moves files to sovereign silos
"""
import argparse
import logging
import os
import shutil
from typing import Any
logging.basicConfig(level=logging.INFO, format='%(message)s')
Logger: Any = logging.getLogger(__name__)

def move_files_to_silos() -> Any:
    """Move Python files from root to appropriate sovereign silos"""
    Logger.info('📁 Moving files to sovereign silos...')
    silo_mappings: Any = {'agentic_core': ['ActionNode', 'agent_logic', 'CognitiveNode', 'ConsensusEngine', 'core_utils', 'action_registry', 'agent_capabilities'], 'apps_lic': ['CanonValidator', 'canon_keys', 'validator', 'canon'], 'apps_rg': ['orchestrator', 'llm_client', 'connection_manager', 'monitor_blackboard'], 'apps_shared': ['db_manager', 'etl_pipeline', 'FactChecker', 'clarity_brevity_filter'], 'scripts': ['clean_duplicates', 'fix_', 'assess_dependencies', 'check_pinecone', 'clear_data', 'canary_monitor', 'bad_actor', 'debug_whitelist'], 'tests': ['test_', 'tests_', '_test']}
    moved_count: Any = 0
    root_files: Any = [f for f in os.listdir('/app') if f.endswith('.py') and os.path.isfile(f'/app/{f}')]
    for filename in root_files:
        if filename in ['entrypoint.sh', 'Dockerfile', 'docker-compose.yml', 'requirements.txt']:
            continue
        target_silo: Any = None
        filename_lower: Any = filename.lower()
        for silo, keywords in silo_mappings.items():
            for keyword in keywords:
                if keyword in filename_lower:
                    target_silo: Any = silo
                    break
            if target_silo:
                break
        if not target_silo:
            target_silo: Any = 'apps_shared'
        silo_path: Any = f'/app/{target_silo}'
        os.makedirs(silo_path, exist_ok=True)
        src_path: Any = f'/app/{filename}'
        dst_path: Any = f'{silo_path}/{filename}'
        try:
            if not os.path.exists(dst_path):
                shutil.move(src_path, dst_path)
                Logger.info(f'📁 Moved {filename} -> {target_silo}/')
                moved_count += 1
        except Exception as e:
            Logger.error(f'❌ Failed to move {filename}: {e}')
    Logger.info(f'\n✨ Moved {moved_count} files to sovereign silos')
    return moved_count

def main() -> Any:
    """Brief description of functionality and purpose."""
    parser: Any = argparse.ArgumentParser(description='Move files to sovereign silos')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be moved without actually moving')
    args: Any = parser.parse_args()
    if args.dry_run:
        Logger.info('🔍 DRY RUN - No files will be moved')
    else:
        move_files_to_silos()
if __name__ == '__main__':
    main()
