#!/usr/bin/env python3
"""Check what the empty layer field means in the ADG."""

import sqlite3
from pathlib import Path

sqlite_path = Path("artifacts/adg/adg_indexed_03222026_1546.sqlite")
if not sqlite_path.exists():
    print("SQLite file not found")
    exit(1)

conn = sqlite3.connect(sqlite_path)
cur = conn.cursor()

# Check empty layer vs L_UNKNOWN
cur.execute("SELECT COUNT(*) FROM nodes WHERE layer = ''")
empty_count = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM nodes WHERE layer = 'L_UNKNOWN'")
unknown_count = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM nodes")
total_count = cur.fetchone()[0]

print(f"Empty layer: {empty_count}")
print(f"L_UNKNOWN: {unknown_count}")
print(f"Total: {total_count}")

# Sample empty layer nodes
cur.execute("""
    SELECT adg_name, entity_type, identity_kind, confidence, resolved_path
    FROM nodes
    WHERE layer = ''
    LIMIT 10
""")
empty_samples = cur.fetchall()

print("\nSample empty layer nodes:")
for name, entity_type, identity_kind, confidence, path in empty_samples:
    print(f"  {name}")
    print(f"    type={entity_type} kind={identity_kind} conf={confidence} path={path}")

conn.close()
