"""Check what layer violations the ADG governance graph actually reports as critical."""

import sqlite3
from pathlib import Path

db = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), reverse=True)[0]
conn = sqlite3.connect(str(db))
conn.row_factory = sqlite3.Row

# Check gravity rules: which layer combos are actually forbidden
# The governance graph edges (GG plane)
rows = conn.execute(
    "SELECT src_id, dst_id, relation_type, source_file, symbol, line_no FROM edges WHERE relation_type IN ('governance_violation','layer_violation','violates') LIMIT 20",
).fetchall()


def node_info(nid):
    r = conn.execute("SELECT adg_name, layer, resolved_path FROM nodes WHERE id=?", (nid,)).fetchone()
    return (r["adg_name"], r["layer"], r["resolved_path"]) if r else (f"<{nid}>", "?", "")


print(f"All governance/violation edges: {len(rows)}")
for r in rows:
    sn, sl, sp = node_info(r["src_id"])
    dn, dl, dp = node_info(r["dst_id"])
    print(f"  type={r['relation_type']}  src_layer={sl}  dst_layer={dl}")
    print(f"    src={sp}")
    print(f"    dst={dp}")
    print(f"    source_file={r['source_file']}  line={r['line_no']}  sym={r['symbol']}")
    print()

# Check what GG (governance) edges exist
rows2 = conn.execute(
    "SELECT relation_type, COUNT(*) as cnt FROM edges WHERE relation_type LIKE '%govern%' OR relation_type LIKE '%violat%' OR relation_type LIKE '%gravity%' GROUP BY relation_type ORDER BY cnt DESC",
).fetchall()
print("GG-type edge counts:")
for r in rows2:
    print(f"  {r['cnt']:5d}  {r['relation_type']}")

conn.close()
print("\nDONE.")
