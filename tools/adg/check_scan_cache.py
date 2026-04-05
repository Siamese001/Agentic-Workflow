#!/usr/bin/env python3
"""Check scan cache for infrastructure modules."""
import json
import glob
import os

# Find scan cache
cache_files = glob.glob('artifacts/adg/cache/scan_result_cache_*.json')
if cache_files:
    latest = max(cache_files, key=os.path.getmtime)
    print(f'Checking: {latest}')
    with open(latest) as f:
        data = json.load(f)
    
    # Find infrastructure entries
    infra_modules = [m for m in data.get('modules', []) if m.get('rel_path', '').startswith('infrastructure/')]
    print(f'\nInfrastructure modules in cache: {len(infra_modules)}')
    for m in infra_modules[:10]:
        rel_path = m.get('rel_path')
        layer = m.get('layer')
        print(f"  - {rel_path} (layer: {layer})")
else:
    print('No scan cache found')
