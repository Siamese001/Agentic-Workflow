#!/usr/bin/env python3
"""Find agents missing heal_repository invocation"""
import json
from archives.location_violations.file_utils import safe_read_file, safe_write_file

with open('agent_discovery_full.json') as f:
    data = json.load(f)

missing = [a for a in data if a.get('invocation') != 'Yes']
print(f"Agents missing heal_repository invocation: {len(missing)}")
for a in missing:
    print(f"  - {a['class_name']}: {a['path']}")
