"""Break down the 207 'violates' edges by src/tgt layer and file."""

import glob
import sqlite3
from collections import Counter

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row

rows = list(
    conn.execute("""
    SELECT n1.layer as src_layer, n1.resolved_path as src_path,
           n2.layer as tgt_layer, n2.resolved_path as tgt_path,
           e.line_no
    FROM edges e
    JOIN nodes n1 ON e.src_id = n1.id
    JOIN nodes n2 ON e.dst_id = n2.id
    WHERE e.relation_type = 'violates'
    ORDER BY n1.layer, n1.resolved_path, e.line_no
"""),
)

print(f"Total 'violates' edges: {len(rows)}\n")

print("--- By src_layer -> tgt_layer ---")
by_pair = Counter((r["src_layer"], r["tgt_layer"]) for r in rows)
for (sl, tl), cnt in sorted(by_pair.items(), key=lambda x: -x[1]):
    print(f"  {cnt:4d}  {sl} -> {tl}")

print("\n--- Top 30 source files ---")
by_file = Counter((r["src_layer"], r["src_path"]) for r in rows)
for (sl, sp), cnt in sorted(by_file.items(), key=lambda x: -x[1])[:30]:
    print(f"  {cnt:3d}  {sl:12s}  {sp}")

conn.close()
