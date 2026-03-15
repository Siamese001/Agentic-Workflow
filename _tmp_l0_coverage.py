import glob
import sqlite3

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
con = sqlite3.connect(db)
cur = con.cursor()

cur.execute(
    "SELECT COUNT(*) FROM edges e JOIN nodes n ON e.src_id=n.id"
    " WHERE e.relation_type IN ('routes_path','routes_through') AND n.layer='L0'"
)
l0_routing = cur.fetchone()[0]

cur.execute(
    "SELECT COUNT(*) FROM edges e JOIN nodes n ON e.src_id=n.id"
    " WHERE e.relation_type='emits_replay_key' AND n.layer='L0'"
)
l0_rk = cur.fetchone()[0]

cur.execute(
    "SELECT COUNT(*) FROM edges e JOIN nodes n ON e.src_id=n.id"
    " WHERE e.relation_type='emits_determinism_digest' AND n.layer='L0'"
)
l0_dd = cur.fetchone()[0]

cur.execute(
    "SELECT COUNT(*) FROM edges e JOIN nodes n ON e.src_id=n.id"
    " WHERE e.relation_type='records_execution_trace' AND n.layer='L0'"
)
l0_rt = cur.fetchone()[0]

cur.execute(
    "SELECT COUNT(*) FROM edges e JOIN nodes n ON e.src_id=n.id"
    " WHERE e.relation_type='signs_execution_trace' AND n.layer='L0'"
)
l0_st = cur.fetchone()[0]

cur.execute(
    "SELECT COUNT(*) FROM edges e JOIN nodes n ON e.src_id=n.id"
    " WHERE e.relation_type='guards_replay' AND n.layer='L0'"
)
l0_gr = cur.fetchone()[0]

print(f"L0 routing_decisions      = {l0_routing}")
print(f"L0 emits_replay_key       = {l0_rk}")
print(f"L0 emits_determinism_dig  = {l0_dd}")
print(f"L0 records_exec_trace     = {l0_rt}")
print(f"L0 signs_exec_trace       = {l0_st}")
print(f"L0 guards_replay          = {l0_gr}")
if l0_routing > 0:
    print(f"L0 replay_coverage        = {l0_rk / l0_routing:.1%}")
    print(f"L0 digest_coverage        = {l0_dd / l0_routing:.1%}")
    print(f"L0 trace_coverage         = {l0_rt / l0_routing:.1%}")

print()
print("invokes_getattr_dynamic in L0 routing engines:")
cur.execute(
    "SELECT e.source_file, e.line_no, e.symbol"
    " FROM edges e JOIN nodes n ON e.src_id=n.id"
    " WHERE e.relation_type='invokes_getattr_dynamic'"
    " AND n.layer='L0'"
    " AND e.source_file LIKE '%L0_routing/engines/%'"
    " ORDER BY e.source_file, e.line_no"
)
for r in cur.fetchall():
    print(f"  {r[0][:70]}  line={r[1]}  sym={r[2]}")

print()
print("uses_wall_clock in L0 prod (non-test):")
cur.execute(
    "SELECT e.source_file, e.line_no, e.symbol"
    " FROM edges e JOIN nodes n ON e.src_id=n.id"
    " WHERE e.relation_type='uses_wall_clock'"
    " AND n.layer='L0'"
    " AND e.source_file NOT LIKE '%test%'"
    " ORDER BY e.source_file, e.line_no"
)
for r in cur.fetchall():
    print(f"  {r[0][:70]}  line={r[1]}  sym={r[2]}")

con.close()
