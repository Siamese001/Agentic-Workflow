"""Show P0 violations detail and authority boundary breaches from ADG SQLite."""

import sqlite3
import glob
import os

adg_dir = r"artifacts\adg"
snapshots = sorted(glob.glob(os.path.join(adg_dir, "adg_indexed_*.sqlite")))
db = snapshots[-1]
print(f"DB: {db}\n")

conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# P0: severity/violation_class breakdown
cur.execute(
    "SELECT severity, violation_class, COUNT(*) as cnt FROM violations GROUP BY severity, violation_class ORDER BY severity, cnt DESC"
)
print("=== violations table breakdown ===")
for r in cur.fetchall():
    print(f"  severity={r['severity']}  class={r['violation_class']}  count={r['cnt']}")

# P0 rows detail
cur.execute(
    "SELECT id, file_path, line_no, severity, violation_class, category, evidence FROM violations WHERE severity='P0' OR violation_class LIKE '%layer%' OR violation_class LIKE '%P0%' LIMIT 20"
)
rows = cur.fetchall()
print(f"\n=== P0 / layer violations ({len(rows)}) ===")
for r in rows:
    print(
        f"  id={r['id']}  file={r['file_path']}:{r['line_no']}  class={r['violation_class']}  cat={r['category']}"
    )
    if r["evidence"]:
        print(f"    evidence: {r['evidence'][:200]}")

# authority boundary breaches (top 5)
cur.execute(
    "SELECT src_file, src_layer, dst_file, dst_layer, relation_type, breach_class FROM mv_authority_boundary_breaches LIMIT 5"
)
print("\n=== mv_authority_boundary_breaches (sample 5) ===")
for r in cur.fetchall():
    print(
        f"  {r['src_layer']}:{r['src_file']} -> {r['dst_layer']}:{r['dst_file']}  rel={r['relation_type']}  breach={r['breach_class']}"
    )

conn.close()
