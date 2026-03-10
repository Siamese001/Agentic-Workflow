#!/usr/bin/env python3
"""Apply fixes until convergence."""

import subprocess
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

for i in range(1, 11):
    print(f"Pass {i}:")
    # Check dry run
    result = subprocess.run(
        [sys.executable, 'ops_scripts/ci/_fix_hardcoded_ssot_literals.py', '--dry-run'],
        capture_output=True, text=True, cwd='.'
    )
    if result.stdout:
        first_line = result.stdout.split('\n')[0]
        print(f"  {first_line}")
    else:
        print("  No output")
        break
    
    # Apply fixes if any
    if '[DRY-RUN] 0 fixes' in result.stdout:
        print("  Converged - no more fixes")
        break
    
    result = subprocess.run(
        [sys.executable, 'ops_scripts/ci/_fix_hardcoded_ssot_literals.py'],
        capture_output=True, text=True, cwd='.'
    )
    if result.returncode != 0:
        print(f"  Error: {result.stderr}")
        break
    print("  Applied fixes")
