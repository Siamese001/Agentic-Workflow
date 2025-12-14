#!/usr/bin/env python3
"""
Comprehensive YAML compliance scanner.
Compares actual folder structure against unified_structure_subatomic.yaml.
import logging

logger = logging.getLogger(__name__)

"""

import yaml
from pathlib import Path

REPO = Path('c:/Git/Agentic-Workflow')

# Map YAML domains to physical folders
DOMAIN_TO_FOLDER = {
    'agentic_core': 'agentic_core',
    'schemas': 'schemas',
    'runtime': 'runtime',
    'prompt_governance': 'prompt_governance',
    'config': 'config',
    'data': '06_data',
    'observability': 'observability',
    'scripts': 'scripts',
    'apps_rg': '09_apps/apps_rg',
    'apps_lic': '09_apps/apps_lic',
    'tests': 'tests',
    'shared_engine_ops': 'shared_engine_ops',
    'shared': 'shared',
}

# Domains to skip for file generation (data contains snapshots, tests are special)
SKIP_DOMAINS = {'data', 'tests'}

def extract_yaml_files(obj: object, prefix: str = '', files: set = None) -> set:
    """Extract all file paths from YAML structure."""
    if files is None:
        files = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.startswith('__'):
                continue
            new_prefix = f'{prefix}/{key}' if prefix else key
            if value is None:  # File (ends with .py)
                files.add(new_prefix)
            elif isinstance(value, dict) and value:
                extract_yaml_files(value, new_prefix, files)
    return files

def get_actual_files(folder_path: str) -> set:
    """Get all Python files in folder, excluding noise."""
    actual = set()
    if not folder_path.exists():
        return actual
    for f in folder_path.rglob('*.py'):
        rel = str(f.relative_to(folder_path)).replace('\\', '/')
        # Skip noise folders
        if any(x in rel for x in ['__pycache__', 'review_pending', 'stub_archive',
                                   '_unassigned', 'YAML', 'phase1_legacy', 'phase3_snapshots']):
            continue
        actual.add(rel)
    return actual

def main() -> None:
    """Main entry point for compliance scan."""
    with open(REPO / 'unified_structure_subatomic.yaml', 'r', encoding='utf-8') as f:
        spec = yaml.safe_load(f)

    total_yaml = 0
    total_actual = 0
    total_missing = 0
    total_extra = 0
    all_missing = []

    for domain, folder in DOMAIN_TO_FOLDER.items():
        if domain not in spec:
            continue

        yaml_files = extract_yaml_files(spec[domain])
        folder_path = REPO / folder
        actual_files = get_actual_files(folder_path)

        missing = yaml_files - actual_files
        extra = actual_files - yaml_files

        total_yaml += len(yaml_files)
        total_actual += len(actual_files)
        total_missing += len(missing)
        total_extra += len(extra)

        (1 - len(missing) / len(yaml_files)) * 100 if yaml_files else 100
        status = 'OK' if len(missing) == 0 else 'GAP'

        if missing and domain not in SKIP_DOMAINS:
            all_missing.extend([(domain, folder, f) for f in sorted(missing)])
            for f in sorted(missing)[:3]:
                logger.info(f"  - {f}")
            if len(missing) > 3:
                logger.info(f"  ... and {len(missing) - 3} more")

    (1 - total_missing / total_yaml) * 100 if total_yaml else 100

    # Summary by priority
    if all_missing:
        by_domain = {}
        for domain, folder, path in all_missing:
            by_domain.setdefault(domain, []).append(path)
        for domain, paths in sorted(by_domain.items()):
            logger.info(f"\n{domain}:")
            for path in paths[:5]:
                logger.info(f"  - {path}")
            if len(paths) > 5:
                logger.info(f"  ... and {len(paths) - 5} more")

    else:
        logger.info("\n✓ All required files present!")

if __name__ == '__main__':
    main()
