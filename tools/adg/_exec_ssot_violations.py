"""List exact import lines in execute_ssot.py causing layer violations."""

import glob
import sqlite3

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row

rows = list(
    conn.execute("""
    SELECT e.line_no, n2.layer as tgt_layer, n2.resolved_path as tgt_path
    FROM edges e
    JOIN nodes n1 ON e.src_id = n1.id
    JOIN nodes n2 ON e.dst_id = n2.id
    WHERE e.relation_type = 'imports'
    AND n1.resolved_path LIKE '%execute_ssot.py'
    AND n2.layer NOT IN ('L0','L_SHARED','L_TOOLS','L_TEST','L_UNKNOWN','')
    ORDER BY e.line_no, n2.layer
"""),
)

seen = set()
for r in rows:
    key = (r["line_no"], r["tgt_layer"], r["tgt_path"])
    if key not in seen:
        seen.add(key)
        print(f"  line {r['line_no']:4d}  {r['tgt_layer']:10s}  {r['tgt_path']}")

conn.close()
