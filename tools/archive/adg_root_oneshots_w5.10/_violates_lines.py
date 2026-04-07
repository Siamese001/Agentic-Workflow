"""Show all remaining violates edges grouped by source file with line numbers."""

import glob
import sqlite3

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row

rows = list(
    conn.execute("""
    SELECT DISTINCT n1.resolved_path as src_path, n1.layer as src_layer,
           e.line_no, n2.layer as tgt_layer, e.symbol as pair
    FROM edges e
    JOIN nodes n1 ON e.src_id = n1.id
    JOIN nodes n2 ON e.dst_id = n2.id
    WHERE e.relation_type = 'violates'
    ORDER BY n1.resolved_path, e.line_no
"""),
)

current = None
for r in rows:
    if r["src_path"] != current:
        current = r["src_path"]
        print(f"\n=== {r['src_layer']:10s}  {r['src_path']} ===")
    print(f"  line {r['line_no']:5d}  -> {r['tgt_layer']:10s}  {r['pair']}")

conn.close()
