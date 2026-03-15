import glob
import sqlite3

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
con = sqlite3.connect(db)
cur = con.cursor()

print("=== emits_determinism_digest sources in L0 ===")
cur.execute(
    "SELECT e.source_file, e.line_no, e.symbol"
    " FROM edges e JOIN nodes n ON e.src_id=n.id"
    " WHERE e.relation_type='emits_determinism_digest'"
    " AND n.layer='L0'"
    " ORDER BY e.source_file, e.line_no"
)
for r in cur.fetchall():
    print(f"  {r[0][-65:]:<67}  line={r[1]}  sym={r[2]}")

print()
print("=== emits_replay_key sources in L0 ===")
cur.execute(
    "SELECT e.source_file, e.line_no, e.symbol"
    " FROM edges e JOIN nodes n ON e.src_id=n.id"
    " WHERE e.relation_type='emits_replay_key'"
    " AND n.layer='L0'"
    " ORDER BY e.source_file, e.line_no"
)
for r in cur.fetchall():
    print(f"  {r[0][-65:]:<67}  line={r[1]}  sym={r[2]}")

print()
print("=== routes_path + routes_through sources in L0 ===")
cur.execute(
    "SELECT e.source_file, e.line_no, e.relation_type, e.symbol"
    " FROM edges e JOIN nodes n ON e.src_id=n.id"
    " WHERE e.relation_type IN ('routes_path','routes_through')"
    " AND n.layer='L0'"
    " ORDER BY e.source_file, e.line_no"
)
for r in cur.fetchall():
    print(f"  {r[0][-65:]:<67}  line={r[1]}  rel={r[2]}  sym={r[3]}")

con.close()
