#!/usr/bin/env python3
"""Catalog all layer gravity violations for wave planning."""

import sqlite3
import glob

files = glob.glob('artifacts/adg/adg_indexed_*.sqlite')
latest = sorted(files)[-1]

conn = sqlite3.connect(latest)
cur = conn.cursor()

# Get detailed list of all layer gravity violations
cur.execute("""
    SELECT evidence, file_path, line_no
    FROM violations
    WHERE evidence LIKE 'L%->L%' AND severity = 'HIGH'
    ORDER BY evidence, file_path
""")

rows = cur.fetchall()

print('=== LAYER GRAVITY VIOLATIONS - DETAILED CATALOG ===')
print(f'Total: {len(rows)} violations')
print()

# Group by violation type
current_type = None
count = 0
for evidence, fp, line in rows:
    if evidence != current_type:
        if current_type:
            print()
        current_type = evidence
        print(f'\n{evidence}:')
        count = 0
    print(f'  {fp}:{line}')
    count += 1

conn.close()
