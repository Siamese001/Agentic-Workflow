#!/usr/bin/env python3
"""Check P4 (LOW severity) violations."""
import sqlite3

conn = sqlite3.connect('artifacts/adg/adg_indexed_03292026_1406.sqlite')
cursor = conn.cursor()

# Get LOW severity violations
cursor.execute("SELECT category, evidence, COUNT(*) FROM violations WHERE severity = 'LOW' GROUP BY evidence ORDER BY COUNT(*) DESC")
low_violations = cursor.fetchall()

print('=== P4 (LOW) Severity Violations ===')
for v in low_violations[:15]:
    print(f'{v[0]} | {v[1]}: {v[2]}')

print(f'\nTotal LOW: {sum(v[2] for v in low_violations)}')
conn.close()
