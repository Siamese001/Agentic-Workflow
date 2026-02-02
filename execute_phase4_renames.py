#!/usr/bin/env python3
"""Execute Phase 4: Rename ADAPTER files to PascalCaseStrategy.py"""
import json
import subprocess
import re
from pathlib import Path

with open('ssot_compliance_report.json', 'r') as f:
    report = json.load(f)

def to_pascal_case(name):
    # Convert snake_case to PascalCase
    parts = name.split('_')
    return ''.join(p.capitalize() for p in parts)

adapters_to_rename = []
for v in report['violations']:
    if v['classification'] != 'ADAPTER':
        continue
    if v['is_naming_compliant']:
        continue
    path = v['path']
    if 'archives' in path.lower():
        continue
    stem = Path(path).stem
    if stem.endswith('Strategy'):
        continue
    adapters_to_rename.append(path)

print(f"Found {len(adapters_to_rename)} ADAPTER files to rename")

def get_new_path(old_path):
    old_file = Path(old_path)
    stem = old_file.stem
    # Convert to PascalCase and add Strategy suffix
    pascal = to_pascal_case(stem.replace('_', ' ').title().replace(' ', ''))
    if not pascal.endswith('Strategy'):
        new_name = f"{pascal}Strategy.py"
    else:
        new_name = f"{pascal}.py"
    return str(old_file.parent / new_name)

renames = []
for old in adapters_to_rename:
    if Path(old).exists():
        renames.append((old, get_new_path(old)))

print(f"Files to rename: {len(renames)}")

success = 0
for old, new in renames:
    try:
        subprocess.run(['git', 'mv', old, new], 
                      capture_output=True, text=True, check=True)
        success += 1
        if success % 20 == 0 or success == len(renames):
            print(f"✓ {success}/{len(renames)} files renamed")
    except subprocess.CalledProcessError as e:
        print(f"✗ {old}: {e.stderr}")

print(f"\n✓ Renamed {success}/{len(renames)} files")
