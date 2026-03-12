import hashlib
import os
from pathlib import Path
from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, get_validated_project_root
from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
PROJECT_ROOT = get_validated_project_root()
GROUPS = {'Location': ['LocationAgent.py', 'LocationValidatorAgent.py', 'LocationHealerAgent.py'], 'Hierarchy': ['HierarchyAgent.py', 'HierarchyValidatorAgent.py'], 'Import': ['ImportAgent.py', 'ImportLockAgent.py'], 'Strategic': ['StrategicRecommendationAgent.py', 'StrategicPlannerAgent.py']}

def get_file_hash(path: Path):
    if not path.exists():
        return None
    return hashlib.md5(path.read_bytes()).hexdigest()

def investigate():
    print('[*] Investigating Potential Overlaps...')
    print(f'[*] Project Root: {PROJECT_ROOT}')
    for group_name, filenames in GROUPS.items():
        print(f'\n--- Group: {group_name} ---')
        found_files = []
        for root, dirs, files in os.walk(PROJECT_ROOT / AGENTIC_CORE_DIR):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            for f in files:
                if f in filenames:
                    found_files.append(Path(root) / f)
        if not found_files:
            print('  No files found.')
            continue
        for f_path in found_files:
            f_hash = get_file_hash(f_path)
            rel_path = f_path.relative_to(PROJECT_ROOT)
            print(f'  Found: {rel_path} (MD5: {f_hash[:8]}...)')
        hashes = [get_file_hash(p) for p in found_files]
        unique_hashes = set(hashes)
        if len(unique_hashes) < len(hashes):
            print('  [!] WARNING: Identical MD5 hashes detected in this group. Consolidation required.')
        else:
            print('  [✓] Implementation patterns differ. Likely intentional separation.')
if __name__ == '__main__':
    investigate()
