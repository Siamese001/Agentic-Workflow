import sqlite3
import glob
from agentic_core.L0_routing.config.path_constants import ADG_ARTIFACTS_DIR

db = sorted(glob.glob(f"{ADG_ARTIFACTS_DIR}/*.sqlite"))[-1]
print("DB:", db)
con = sqlite3.connect(db)
cur = con.cursor()

cur.execute(
    "SELECT family_name, relation_type, plumbing_witness_count, test_witness_count,"
    " live_runtime_witness_count, runtime_orphaned"
    " FROM mv_cross_cutting_witness_tiers"
    " WHERE family_name = 'future_run_only_promotion'"
    " ORDER BY relation_type"
)
rows = cur.fetchall()
con.close()

print()
print(f"  {'relation_type':<35} {'plumbing':>8} {'test':>6} {'live_rt':>8} {'orphaned':>9}")
print("  " + "-" * 75)
tot_p, tot_t, tot_l = 0, 0, 0
for fam, rel, p, t, live, orph in rows:
    print(f"  {rel:<35} {p:>8} {t:>6} {live:>8} {str(bool(orph)):>9}")
    tot_p += p
    tot_t += t
    tot_l += live
print("  " + "-" * 75)
status = "PASSED" if tot_l > 0 else "WARN(orphan)"
label = "TOTAL"
print(f"  {label:<35} {tot_p:>8} {tot_t:>6} {tot_l:>8} {str(tot_l == 0):>9}  ci_status={status}")
