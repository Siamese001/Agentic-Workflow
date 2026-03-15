import glob
import sqlite3

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
con = sqlite3.connect(db)
cur = con.cursor()
print(f"DB: {db}\n")

print("=== CURRENT L1 SIGNAL BASELINE (runtime non-test) ===")
for sig in [
    "records_execution_trace",
    "signs_execution_trace",
    "transcripts_response",
    "references_policy_hash",
    "hard_fails_untranscripted",
    "emits_replay_key",
    "routes_path",
    "routes_through",
]:
    cur.execute(
        "SELECT COUNT(*) FROM edges WHERE relation_type=?"
        " AND source_file NOT LIKE '%test%'"
        " AND source_file NOT LIKE '%tests%'"
        " AND source_file NOT LIKE '%spec%'"
        " AND source_file NOT LIKE '%mock%'",
        (sig,),
    )
    total = cur.fetchone()[0]
    cur.execute(
        "SELECT COUNT(*) FROM edges e JOIN nodes n ON e.src_id=n.id"
        " WHERE e.relation_type=? AND n.layer='L1'"
        " AND e.source_file NOT LIKE '%test%'"
        " AND e.source_file NOT LIKE '%tests%'",
        (sig,),
    )
    l1 = cur.fetchone()[0]
    print(f"  {sig:<40} runtime_total={total:4d}  L1_runtime={l1:3d}")

print()
print("=== L1 ENGINE FILES ===")
cur.execute(
    "SELECT DISTINCT resolved_path FROM nodes"
    " WHERE layer='L1' AND entity_type='module'"
    " AND resolved_path NOT LIKE '%test%'"
    " ORDER BY resolved_path"
)
for r in cur.fetchall():
    print(f"  {r[0]}")

print()
print("=== L1 RUNTIME REASONING CALL SITES ===")
cur.execute(
    "SELECT e.source_file, e.line_no, e.relation_type, e.symbol"
    " FROM edges e JOIN nodes n ON e.src_id=n.id"
    " WHERE n.layer='L1'"
    " AND e.relation_type IN ('records_execution_trace','signs_execution_trace',"
    "  'transcripts_response','references_policy_hash')"
    " AND e.source_file NOT LIKE '%test%'"
    " ORDER BY e.source_file, e.line_no"
)
for r in cur.fetchall():
    print(f"  {r[0][-65:]:<67}  line={r[1]}  rel={r[2]}  sym={r[3]}")

print()
print("=== L1 WALL CLOCK / DYNAMIC DISPATCH ===")
cur.execute(
    "SELECT e.source_file, e.line_no, e.relation_type, e.symbol"
    " FROM edges e JOIN nodes n ON e.src_id=n.id"
    " WHERE n.layer='L1'"
    " AND e.relation_type IN ('uses_wall_clock','invokes_getattr_dynamic')"
    " AND e.source_file NOT LIKE '%test%'"
    " ORDER BY e.source_file, e.line_no"
)
for r in cur.fetchall():
    print(f"  {r[0][-65:]:<67}  line={r[1]}  rel={r[2]}  sym={r[3]}")

print()
print("=== TRANSCRIPTS_RESPONSE / REFERENCES_POLICY_HASH in schema ===")
for sym in [
    "TRANSCRIPT",
    "POLICY_HASH",
    "transcripts_response",
    "references_policy_hash",
    "hard_fails_untranscripted",
]:
    cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type LIKE ?", (f"%{sym}%",))
    print(f"  edges with rel LIKE '{sym}': {cur.fetchone()[0]}")

con.close()
