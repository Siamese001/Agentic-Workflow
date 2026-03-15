import glob
import sqlite3

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
con = sqlite3.connect(db)
cur = con.cursor()
print(f"DB: {db}\n")

EXCL_E = (
    "AND e.source_file NOT LIKE '%test%' "
    "AND e.source_file NOT LIKE '%tests%' "
    "AND e.source_file NOT LIKE '%spec%' "
    "AND e.source_file NOT LIKE '%fixture%' "
    "AND e.source_file NOT LIKE '%mock%'"
)

print("=== L1 runtime signal edges (all, not distinct) ===")
for sig in [
    "records_execution_trace",
    "signs_execution_trace",
    "transcripts_response",
    "references_policy_hash",
    "hard_fails_untranscripted",
]:
    cur.execute(
        f"SELECT e.source_file, e.line_no, e.symbol FROM edges e JOIN nodes n ON e.src_id=n.id"
        f" WHERE n.layer='L1' AND e.relation_type=? {EXCL_E}"
        f" ORDER BY e.source_file, e.line_no",
        (sig,),
    )
    rows = cur.fetchall()
    print(f"\n  {sig} ({len(rows)} edges):")
    for r in rows:
        print(f"    {r[0][-65:]:<67} line={r[1]} sym={r[2]}")

print()
print("=== reasoning_chokepoint.py node (what layer?) ===")
cur.execute(
    "SELECT id, adg_name, layer, resolved_path FROM nodes WHERE resolved_path LIKE '%reasoning_chokepoint%'"
)
for r in cur.fetchall():
    print(f"  id={r[0]} name={r[1]} layer={r[2]} path={r[3]}")

print()
print("=== reasoning_chokepoint.py edges ===")
cur.execute(
    "SELECT e.relation_type, e.line_no, e.symbol FROM edges e JOIN nodes n ON e.src_id=n.id"
    " WHERE n.resolved_path LIKE '%reasoning_chokepoint%'"
    " ORDER BY e.relation_type, e.line_no"
)
for r in cur.fetchall():
    print(f"  rel={r[0]:<40} line={r[1]} sym={r[2]}")

print()
print("=== CognitiveNode.py / cognitive_engine.py edges ===")
for fname in ["CognitiveNode", "cognitive_engine", "capability_analyzer"]:
    cur.execute(
        "SELECT e.relation_type, e.line_no, e.symbol FROM edges e JOIN nodes n ON e.src_id=n.id"
        f" WHERE n.resolved_path LIKE '%{fname}%'"
        " AND e.relation_type IN ('records_execution_trace','signs_execution_trace',"
        "  'transcripts_response','references_policy_hash','hard_fails_untranscripted')"
        " ORDER BY e.relation_type, e.line_no"
    )
    rows = cur.fetchall()
    print(f"\n  {fname} ({len(rows)} trace edges):")
    for r in rows:
        print(f"    rel={r[0]:<40} line={r[1]} sym={r[2]}")

print()
print("=== What does scanner detect from reason_and_record call? ===")
cur.execute(
    "SELECT e.source_file, e.relation_type, e.line_no, e.symbol FROM edges"
    " WHERE symbol LIKE '%reason_and_record%'"
    " ORDER BY source_file"
)
for r in cur.fetchall():
    print(f"  {r[0][-60:]:<62} rel={r[1]} line={r[2]} sym={r[3]}")

con.close()
