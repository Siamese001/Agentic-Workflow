#!/usr/bin/env python3
"""Recategorize layer gravity violations to HIGH severity."""

import sqlite3
import glob

# Find latest ADG
files = glob.glob('artifacts/adg/adg_indexed_*.sqlite')
latest = sorted(files)[-1]

print(f'ADG: {latest}')
print()

conn = sqlite3.connect(latest)
cur = conn.cursor()

# Find all layer gravity violations
cur.execute("""
    SELECT id, file_path, line_no, evidence, severity
    FROM violations
    WHERE evidence LIKE 'L%->L%'
    ORDER BY evidence, file_path
""")

rows = cur.fetchall()
print(f'Found {len(rows)} layer gravity violations')

# Update all to HIGH severity
cur.execute("UPDATE violations SET severity = 'HIGH' WHERE evidence LIKE 'L%->L%'")
conn.commit()

# Verify update
cur.execute("SELECT COUNT(*) FROM violations WHERE evidence LIKE 'L%->L%' AND severity = 'HIGH'")
high_count = cur.fetchone()[0]
print(f'Updated {high_count} violations to HIGH severity')
print()

# Show breakdown
cur.execute("""
    SELECT evidence, COUNT(*) as cnt
    FROM violations
    WHERE evidence LIKE 'L%->L%'
    GROUP BY evidence
    ORDER BY cnt DESC
""")

print('=== LAYER GRAVITY VIOLATIONS (Now HIGH Severity) ===')
print()
print(f'{"Violation Type":<30} {"Count":>5}')
print('-' * 40)
for evidence, cnt in cur.fetchall():
    print(f'{evidence:<30} {cnt:>5}')

conn.close()
print()
print('All layer gravity violations now HIGH severity.')
