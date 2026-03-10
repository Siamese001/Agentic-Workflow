#!/usr/bin/env python3
"""Test fixer directly on the specific file."""

import sys
sys.path.insert(0, '.')
from pathlib import Path
from ops_scripts.ci._fix_hardcoded_ssot_literals import process_file

file_path = Path('agentic_core/L0_routing/utils/scorched_earth_merge_util.py')
dry_run = True

fixes = process_file(file_path, str(file_path), dry_run=dry_run)

print(f'Found {len(fixes)} fixes:')
for fix in fixes:
    print(f'  {fix}')
