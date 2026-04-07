import glob
import sqlite3

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
viols = list(
    conn.execute(
        "SELECT n1.adg_name as src, n2.adg_name as dst, e.edge_kind, e.source_file, e.line_no "
        "FROM edges e JOIN nodes n1 ON e.src_id=n1.id JOIN nodes n2 ON e.dst_id=n2.id "
        "WHERE e.relation_type='violates'",
    ),
)
print(f"GV_violates: {len(viols)}")
for v in viols:
    print(f"  {v['src']} -> {v['dst']}  ({v['edge_kind']})  @{v['source_file']}:{v['line_no']}")
conn.close()
