"""Query L0_routing violations from ADG index."""

import pathlib
import sqlite3

DB = pathlib.Path("artifacts/adg/adg_indexed_03122026.sqlite")
conn = sqlite3.connect(DB)

print("=== L0_routing violations ===")
rows = conn.execute(
    "SELECT e.source_file, e.symbol, e.line_no FROM edges e "
    "WHERE e.relation_type='violates' AND e.source_file LIKE '%L0_routing%' "
    "ORDER BY e.source_file, e.line_no",
).fetchall()
for r in rows:
    print(f"{r[0]}:{r[2]}  {r[1]}")

print(f"\nTotal: {len(rows)}")

print("\n=== L0_routing violations by file ===")
rows2 = conn.execute(
    "SELECT e.source_file, COUNT(*) as cnt FROM edges e "
    "WHERE e.relation_type='violates' AND e.source_file LIKE '%L0_routing%' "
    "GROUP BY e.source_file ORDER BY cnt DESC",
).fetchall()
for r in rows2:
    print(f"  {r[1]:3d}  {r[0]}")

conn.close()
