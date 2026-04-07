"""Survey all GV_violates edges grouped by src_layer -> tgt_layer and src_path."""

import glob
import sqlite3
from collections import Counter

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
print(f"DB: {db}")
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row

# Gravity rules encoded in ADG: LN can only import from L0..LN
# Violation = edge where tgt layer is higher than src layer
LAYER_RANK = {
    "L0": 0,
    "L_TOOLS": 0,
    "L_SHARED": 0,
    "L1": 1,
    "L_RUNTIME": 1,
    "L2": 2,
    "L_PG": 2,
    "L3": 3,
    "L4": 4,
    "L5": 5,
    "L6": 6,
    "L_APP": 7,
    "L_SL": 8,
    "L_TEST": -1,
    "L_UNKNOWN": -1,
    "": -1,
}

rows = list(
    conn.execute("""
    SELECT e.src_id, e.dst_id, e.line_no,
           n1.layer as src_layer, n1.resolved_path as src_path,
           n2.layer as tgt_layer, n2.resolved_path as tgt_path
    FROM edges e
    JOIN nodes n1 ON e.src_id = n1.id
    JOIN nodes n2 ON e.dst_id = n2.id
    WHERE e.relation_type = 'imports'
    AND n1.layer NOT IN ('L_TEST','L_UNKNOWN','L_TOOLS','L_APP','L_SL','')
    AND n2.layer NOT IN ('L_TEST','L_UNKNOWN','','L0','L_SHARED')
"""),
)

violations = []
for r in rows:
    src_rank = LAYER_RANK.get(r["src_layer"], -1)
    tgt_rank = LAYER_RANK.get(r["tgt_layer"], -1)
    if src_rank >= 0 and tgt_rank > src_rank:
        violations.append((r["src_layer"], r["src_path"], r["tgt_layer"], r["tgt_path"], r["line_no"]))

print(f"\nTotal module-level-equivalent violations: {len(violations)}")
print("\n--- By src_layer -> tgt_layer ---")
by_pair = Counter((sl, tl) for sl, _, tl, _, _ in violations)
for (sl, tl), cnt in sorted(by_pair.items(), key=lambda x: -x[1]):
    print(f"  {cnt:4d}  {sl} -> {tl}")

print("\n--- Top 30 files ---")
by_file = Counter((sl, sp, tl) for sl, sp, tl, _, _ in violations)
for (sl, sp, tl), cnt in sorted(by_file.items(), key=lambda x: -x[1])[:30]:
    print(f"  {cnt:3d}  {sl}->{tl:10s}  {sp}")
conn.close()
