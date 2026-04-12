#!/usr/bin/env python3
"""Check L_UNKNOWN growth and analyze what's being classified as unknown."""

import sqlite3
from pathlib import Path

adg_dir = Path("artifacts/adg")
sqlite_candidates = sorted(adg_dir.glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime)
sqlite_path = sqlite_candidates[-1] if sqlite_candidates else None

if not sqlite_path or not sqlite_path.exists():
    print("SQLite file not found")
    exit(1)

print(f"Using SQLite: {sqlite_path.name}")

conn = sqlite3.connect(sqlite_path)
cur = conn.cursor()

# Overall stats
cur.execute("SELECT COUNT(*) FROM nodes WHERE layer = 'L_UNKNOWN'")
unknown_count = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM nodes")
total_count = cur.fetchone()[0]

cur.execute("SELECT layer, COUNT(*) FROM nodes GROUP BY layer ORDER BY COUNT(*) DESC")
layers = cur.fetchall()

print(f"L_UNKNOWN: {unknown_count}/{total_count} ({unknown_count / total_count * 100:.1f}%)")
print("\nLayer distribution:")
for layer, count in layers:
    pct = count / total_count * 100
    print(f"  {layer}: {count} ({pct:.1f}%)")

# Sample unknown nodes
cur.execute("""
    SELECT adg_name, entity_type, identity_kind, confidence, resolved_path
    FROM nodes
    WHERE layer = 'L_UNKNOWN'
    ORDER BY adg_name
    LIMIT 20
""")
unknown_samples = cur.fetchall()

print(f"\nSample L_UNKNOWN nodes ({len(unknown_samples)} of {unknown_count}):")
for name, entity_type, identity_kind, confidence, path in unknown_samples:
    print(f"  {name}")
    print(f"    type={entity_type} kind={identity_kind} conf={confidence} path={path}")

# Check patterns
cur.execute("""
    SELECT
        SUBSTR(resolved_path, 1, 3) as prefix,
        COUNT(*) as count
    FROM nodes
    WHERE layer = 'L_UNKNOWN'
    GROUP BY prefix
    ORDER BY count DESC
""")
patterns = cur.fetchall()

print("\nL_UNKNOWN by path prefix:")
for prefix, count in patterns:
    print(f"  {prefix}/*: {count}")

conn.close()
