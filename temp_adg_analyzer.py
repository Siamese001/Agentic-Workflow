#!/usr/bin/env python3
"""Analyze ADG to find test import/dependency errors."""
import json
from pathlib import Path
from collections import defaultdict

# Load the latest ADG
adg_path = Path('artifacts/adg/adg_full_20260310T012640Z.json')
with open(adg_path, 'r') as f:
    adg = json.load(f)

# Find test files with import errors
test_errors = []
error_types = defaultdict(list)

for node_id, node_data in adg.get('nodes', {}).items():
    if 'tests/' in node_id and node_data.get('errors'):
        errors = node_data['errors']
        for error in errors:
            if 'import' in error.lower() or 'module' in error.lower() or 'nameerror' in error.lower():
                test_errors.append({
                    'file': node_id,
                    'error': error
                })
                # Categorize error
                if 'cannot import' in error.lower():
                    error_types['cannot_import'].append(node_id)
                elif 'no module named' in error.lower():
                    error_types['no_module'].append(node_id)
                elif 'nameerror' in error.lower():
                    error_types['nameerror'].append(node_id)
                else:
                    error_types['other'].append(node_id)

print(f'Found {len(test_errors)} test files with import/dependency errors\n')

print('Error Type Breakdown:')
for error_type, files in error_types.items():
    print(f'  {error_type}: {len(files)} files')

print('\n=== Top 30 Import Errors ===')
for i, err in enumerate(test_errors[:30], 1):
    print(f'\n{i}. {err["file"]}')
    print(f'   {err["error"][:150]}')
