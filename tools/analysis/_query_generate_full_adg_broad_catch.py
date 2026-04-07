#!/usr/bin/env python3
"""Query specific broad_exception_catch violations in generate_full_adg.py."""
import sqlite3
from pathlib import Path

adg_dir = Path(__file__).resolve().parents[2] / "artifacts" / "adg"
dbs = sorted([p for p in adg_dir.glob("adg_indexed_*.sqlite") if p.stat().st_size > 0], key=lambda p: p.stat().st_mtime, reverse=True)
db = dbs[0]

conn = sqlite3.connect(db)
cur = conn.cursor()

print("=== broad_exception_catch in tools/adg/shared_modules/extracted_training_pipeline.py ===")
rows = conn.execute(
    """SELECT e.source_file, e.line_no, e.edge_kind
       FROM violations v JOIN edges e ON v.edge_id=e.id
       WHERE e.edge_kind='broad_exception_catch'
       AND e.source_file LIKE '%extracted_training_pipeline.py'
       ORDER BY e.line_no"""
).fetchall()

for row in rows:
    print(f"{row[0]}:{row[1]}  sym={row[2]}")

print("\n=== return_none_swallow in tools/adg/shared_modules/extracted_training_pipeline.py ===")
rows2 = conn.execute(
    """SELECT e.source_file, e.line_no, e.edge_kind
       FROM violations v JOIN edges e ON v.edge_id=e.id
       WHERE e.edge_kind='return_none_swallow'
       AND e.source_file LIKE '%extracted_training_pipeline.py'
       ORDER BY e.line_no"""
).fetchall()

for row in rows:
    print(f"{row[0]}:{row[1]}  sym={row[2]}")

conn.close()
