#!/usr/bin/env python3
"""Execute Phase 2: Rename TYPES files to snake_case_types.py"""
import json
import subprocess
import re
from pathlib import Path

with open('ssot_compliance_report.json', 'r') as f:
    report = json.load(f)

def to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

types_to_rename = []
for v in report['violations']:
    if v['classification'] != 'TYPES':
        continue
    if v['is_naming_compliant']:
        continue
    path = v['path']
    if 'archives' in path.lower():
        continue
    stem = Path(path).stem
    if stem.endswith('_types'):
        continue
    types_to_rename.append(path)

print(f"Found {len(types_to_rename)} TYPES files to rename")

def get_new_path(old_path):
    old_file = Path(old_path)
    snake = to_snake_case(old_file.stem)
    if not snake.endswith('_types'):
        new_name = f"{snake}_types.py"
    else:
        new_name = f"{snake}.py"
    return str(old_file.parent / new_name)

renames = []
for old in types_to_rename:
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
