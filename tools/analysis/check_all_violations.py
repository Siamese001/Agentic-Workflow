#!/usr/bin/env python3
"""Check updated ADG violation counts after regeneration."""
import sqlite3
from pathlib import Path

# Find latest ADG SQLite
adg_dir = Path('artifacts/adg')
sqlite_files = sorted(adg_dir.glob('adg_indexed_*.sqlite'), reverse=True)
if not sqlite_files:
    print('No ADG SQLite found')
    exit(1)

latest = sqlite_files[0]
print(f'Using: {latest.name}')

conn = sqlite3.connect(latest)
cursor = conn.cursor()

# Get violations by severity
cursor.execute("SELECT severity, COUNT(*) FROM violations GROUP BY severity")
by_severity = cursor.fetchall()
print('\n=== Violations by Severity ===')
for sev, count in by_severity:
    print(f'  {sev}: {count}')

# Get HIGH violations detail
cursor.execute("SELECT file_path, line_no, evidence FROM violations WHERE severity = 'HIGH' ORDER BY file_path")
high = cursor.fetchall()
if high:
    print(f'\n=== HIGH Severity Violations ({len(high)}) ===')
    for v in high[:15]:
        print(f'  {v[0]}:{v[1]} - {v[2]}')
    if len(high) > 15:
        print(f'  ... and {len(high) - 15} more')
else:
    print('\n=== NO HIGH Severity Violations ===')

# Get total
total = sum(c for _, c in by_severity)
print(f'\n=== TOTAL VIOLATIONS: {total} ===')

conn.close()
