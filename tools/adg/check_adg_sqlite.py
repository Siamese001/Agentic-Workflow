#!/usr/bin/env python3
"""Check ADG SQLite for infrastructure modules."""
import sqlite3
import glob
import os

# Find latest ADG
adg_dir = 'artifacts/adg'
sqlite_files = glob.glob(f'{adg_dir}/adg_indexed_*.sqlite')
latest = max(sqlite_files, key=os.path.getmtime)
print(f'Latest ADG: {latest}')

conn = sqlite3.connect(latest)
cursor = conn.cursor()

# Check total modules
cursor.execute('SELECT COUNT(*) FROM nodes WHERE entity_type = "module"')
total = cursor.fetchone()[0]
print(f'Total modules: {total}')

# Check for any infrastructure references
cursor.execute("SELECT resolved_path FROM nodes WHERE resolved_path LIKE '%infrastructure%' LIMIT 10")
rows = cursor.fetchall()
print(f'Infrastructure references: {len(rows)}')
for r in rows:
    print(f'  {r[0]}')

# Check layer distribution
print('\nLayer distribution:')
cursor.execute('SELECT layer, COUNT(*) FROM nodes WHERE entity_type = "module" GROUP BY layer ORDER BY COUNT(*) DESC')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

conn.close()
