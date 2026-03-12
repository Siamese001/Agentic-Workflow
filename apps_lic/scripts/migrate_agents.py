import os
import shutil
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
from pathlib import Path

def migrate_rescued_agents() -> None:
    """
    Moves the enriched agents from legacy_archive to the apps_lic/engines SSOT.
    """
    # guardian: allow-path-string
    base_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
    source_dir = Path(base_dir) / 'legacy_archive'
    target_dir = Path(base_dir) / 'engines'
    os.makedirs(target_dir, exist_ok=True)
    init_path = Path(target_dir) / '__init__.py'
    # guardian: allow-path-string
    if not os.path.exists(init_path):
        with open(init_path, 'w', encoding='utf-8') as handle:
            handle.write('"""SSOT Agents Package generated during migration."""\n')
    files_to_move = ['CompetitorReconAgent.py', 'StackModernizationAgent.py']
    for filename in files_to_move:
        src = Path(source_dir) / filename
        dst = Path(target_dir) / filename
        # guardian: allow-path-string
        if os.path.exists(src):
            # guardian: allow-path-string
            if os.path.exists(dst):
                print(f'WARNING: Target {filename} already exists in engines/. Overwriting with Enriched version.')
            shutil.move(src, dst)
            print(f'SUCCESS: Moved {filename} to {target_dir}')
        else:
            print(f'ERROR: Source file {filename} not found in archive.')
if __name__ == '__main__':
    migrate_rescued_agents()
