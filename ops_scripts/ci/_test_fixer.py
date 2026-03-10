#!/usr/bin/env python3
"""Test fixer directly on the specific file."""

import sys
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

sys.path.insert(0, '.')
from pathlib import Path
from ops_scripts.ci._fix_hardcoded_ssot_literals import process_file

file_path = Path('agentic_core/L0_routing/utils/scorched_earth_merge_util.py')
dry_run = True

fixes = process_file(file_path, str(file_path), dry_run=dry_run)

print(f'Found {len(fixes)} fixes:')
for fix in fixes:
    print(f'  {fix}')
