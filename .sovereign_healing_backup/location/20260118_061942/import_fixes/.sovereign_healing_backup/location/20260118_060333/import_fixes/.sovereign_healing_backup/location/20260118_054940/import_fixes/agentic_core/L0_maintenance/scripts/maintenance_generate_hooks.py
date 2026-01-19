from __future__ import annotations
"""
Pre-commit Hook Generator - SSOT Synchronization
Dynamically generates .pre-commit-config.yaml patterns from structure_blueprint.py
to eliminate hardcoded folder lists and prevent drift.

Usage:
    python scripts/maintenance/generate_hooks.py
    python scripts/maintenance/generate_hooks.py --dry-run
"""
import sys
from pathlib import Path
import re
from typing import Any
project_root: Any = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))
from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_REGISTRY

def sync_pre_commit(dry_run: bool=False) -> Any:
    """
    Synchronize .pre-commit-config.yaml with SSOT from structure_blueprint.py
    
    Args:
        dry_run: If True, only print changes without modifying files
    """
    sovereign_roots: Any = list(SOVEREIGN_REGISTRY.keys())
    system_folders: Any = ['data', 'archives']
    all_roots: Any = sovereign_roots + system_folders
    roots_pattern: Any = '|'.join(sovereign_roots)
    all_roots_pattern: Any = '|'.join(all_roots)
    exclude_pattern: Any = f'^({all_roots_pattern})/'
    files_pattern: Any = f'^({roots_pattern})/.*\\.py$'
    print(f'[*] Syncing Pre-commit Config with SSOT...')
    print(f"   [SSOT] Sovereign Roots: {', '.join(sovereign_roots)}")
    print(f'   [PATTERN] Exclude: {exclude_pattern}')
    print(f'   [PATTERN] Files: {files_pattern}')
    config_path: Any = project_root / 'agentic_core' / 'L0_maintenance' / 'scripts' / '.pre-commit-config.yaml'
    if not config_path.exists():
        print(f'   [!] Config not found at: {config_path}')
        print(f'   [!] Checking alternate location...')
        config_path: Any = project_root / '.pre-commit-config.yaml'
        if not config_path.exists():
            print(f'   [X] No .pre-commit-config.yaml found!')
            return False
    print(f'   [OK] Found config at: {config_path}')
    with open(config_path, 'r', encoding='utf-8') as f:
        content: Any = f.read()
    original_content: Any = content
    replacements: Any = [('exclude: \\^[(]agentic_core\\|apps_lic\\|apps_rg\\|apps_shared\\|schemas\\|prompt_governance\\|observability\\|config\\|data\\|archives[)]/', f'exclude: ^({all_roots_pattern})/'), ('files: \\^[(]agentic_core\\|apps_lic\\|apps_rg\\|apps_shared\\|schemas\\|prompt_governance\\|observability\\|config[)]/\\.\\*\\\\\\.py\\$', f'files: ^({roots_pattern})/.*\\.py$')]
    changes_made: Any = 0
    for pattern, replacement in replacements:
        matches: Any = re.findall(pattern, content)
        if matches:
            content: Any = re.sub(pattern, replacement, content)
            changes_made += len(matches)
            print(f'   [✓] Updated {len(matches)} pattern(s)')
    if changes_made == 0:
        print(f'   [OK] No changes needed - config already synchronized')
        return True
    if dry_run:
        print(f'\n   [DRY-RUN] Would update {changes_made} pattern(s)')
        print(f'\n--- DIFF ---')
        print(f'Original patterns found, would be replaced with SSOT-derived patterns')
        return True
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'   [✓] Updated {changes_made} pattern(s) in {config_path.name}')
    print(f'   [SUCCESS] Pre-commit config synchronized with SSOT')
    return True

def generate_sovereign_list() -> Any:
    """Generate a formatted list of sovereign roots for documentation"""
    sovereign_roots: Any = list(SOVEREIGN_REGISTRY.keys())
    print('\n[SSOT] Current Sovereign Registry:')
    for i, root in enumerate(sovereign_roots, 1):
        depth: Any = SOVEREIGN_REGISTRY[root]['depth']
        subfolders: Any = len(SOVEREIGN_REGISTRY[root]['subfolders'])
        print(f'  {i:2d}. {root:<25} (Depth: {depth}, Subfolders: {subfolders})')
    print(f'\nTotal: {len(sovereign_roots)} sovereign roots')
if __name__ == '__main__':
    import argparse
    parser: Any = argparse.ArgumentParser(description='Sync pre-commit config with SSOT')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
    parser.add_argument('--list', action='store_true', help='List current sovereign roots')
    args: Any = parser.parse_args()
    if args.list:
        generate_sovereign_list()
    else:
        success: Any = sync_pre_commit(dry_run=args.dry_run)
        sys.exit(0 if success else 1)
