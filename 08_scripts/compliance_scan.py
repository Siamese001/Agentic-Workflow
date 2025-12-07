#!/usr/bin/env python3
"""
Comprehensive YAML compliance scanner.
Compares actual folder structure against unified_structure_subatomic.yaml.
"""

import yaml
from pathlib import Path

REPO = Path('c:/Git/Agentic-Workflow')

# Map YAML domains to physical folders
DOMAIN_TO_FOLDER = {
    'agentic_core': '01_agentic_core',
    'schemas': '02_schemas',
    'runtime': '03_runtime',
    'prompt_governance': '04_prompt_governance',
    'config': '05_config',
    'data': '06_data',
    'observability': '07_observability',
    'scripts': '08_scripts',
    'apps_rg': '09_apps/apps_rg',
    'apps_lic': '09_apps/apps_lic',
    'tests': '10_tests',
    'shared_engine_ops': 'shared_engine_ops',
    'shared': 'shared',
}

# Domains to skip for file generation (data contains snapshots, tests are special)
SKIP_DOMAINS = {'data', 'tests'}


def extract_yaml_files(obj, prefix='', files=None):
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


def get_actual_files(folder_path):
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


def main():
    with open(REPO / 'unified_structure_subatomic.yaml', 'r', encoding='utf-8') as f:
        spec = yaml.safe_load(f)

    print('=' * 80)
    print('COMPREHENSIVE YAML COMPLIANCE SCAN')
    print('=' * 80)

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
        
        coverage = (1 - len(missing) / len(yaml_files)) * 100 if yaml_files else 100
        status = 'OK' if len(missing) == 0 else 'GAP'
        
        print(f'\n[{domain.upper()}] {folder}')
        print(f'  YAML: {len(yaml_files):>4}  Actual: {len(actual_files):>4}  Missing: {len(missing):>4}  Extra: {len(extra):>4}  [{status}] {coverage:.0f}%')
        
        if missing and domain not in SKIP_DOMAINS:
            all_missing.extend([(domain, folder, f) for f in sorted(missing)])
            for f in sorted(missing)[:3]:
                print(f'    MISSING: {f}')
            if len(missing) > 3:
                print(f'    ... and {len(missing) - 3} more')

    print('\n' + '=' * 80)
    overall = (1 - total_missing / total_yaml) * 100 if total_yaml else 100
    print(f'TOTAL: YAML={total_yaml}  Actual={total_actual}  Missing={total_missing}  Extra={total_extra}  Coverage={overall:.1f}%')
    print('=' * 80)

    # Summary by priority
    if all_missing:
        print(f'\nMISSING FILES BY DOMAIN (excluding {SKIP_DOMAINS}):')
        by_domain = {}
        for domain, folder, path in all_missing:
            by_domain.setdefault(domain, []).append(path)
        for domain, paths in sorted(by_domain.items()):
            print(f'  {domain}: {len(paths)} files')
    else:
        print('\nALL DOMAINS AT 100% COVERAGE!')


if __name__ == '__main__':
    main()
