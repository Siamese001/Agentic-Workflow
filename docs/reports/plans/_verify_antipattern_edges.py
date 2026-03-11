"""Verify antipattern edges appear in the latest ADG SQLite database."""

import glob
import os
import sqlite3

files = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))
if not files:
    print("ERROR: No ADG sqlite files found")
    raise SystemExit(1)

db = files[-1]
print(f"DB: {os.path.basename(db)}")
con = sqlite3.connect(db)

counts = con.execute("""
    SELECT edge_kind, COUNT(*) as cnt
    FROM edges
    WHERE relation_type = 'antipattern'
    GROUP BY edge_kind
    ORDER BY cnt DESC
""").fetchall()

print("Antipattern edge counts:")
for kind, cnt in counts:
    print(f"  {kind}: {cnt}")

total = con.execute("SELECT COUNT(*) FROM edges WHERE relation_type='antipattern'").fetchone()[0]
print(f"Total antipattern edges: {total}")

sample = con.execute("""
    SELECT source_file, line_no, edge_kind, symbol
    FROM edges
    WHERE relation_type = 'antipattern'
    ORDER BY edge_kind, source_file, line_no
    LIMIT 12
""").fetchall()
print("Sample edges:")
for row in sample:
    print(f"  {row[2]:<35s} {row[0]}:{row[1]}  [{row[3]}]")

manifest = con.execute("""
    SELECT antipattern_count
    FROM manifests
    ORDER BY rowid DESC
    LIMIT 1
""").fetchone()
if manifest:
    print(f"Manifest antipattern_count: {manifest[0]}")
else:
    print("No manifest row found (may be stored elsewhere)")

con.close()
