#!/usr/bin/env python3
"""STEP 0-1: Scope lock and gap detection."""

import glob
import sqlite3

files = glob.glob('artifacts/adg/adg_indexed_*.sqlite')
latest = sorted(files)[-1]

conn = sqlite3.connect(latest)
cur = conn.cursor()

# Check layer gravity violations
cur.execute("SELECT evidence, file_path, line_no FROM violations WHERE evidence LIKE 'L%->L%' AND severity = 'HIGH' ORDER BY evidence, file_path")

rows = cur.fetchall()
print(f'GAPS_FOUND: {len(rows)}')
print()

current_type = None
for evidence, fp, line in rows:
    if evidence != current_type:
        print(f'{evidence}:')
        current_type = evidence
    print(f'  {fp}:{line}')

conn.close()
