"""L2 execution layer baseline audit for P0/L2 guardrail closure."""

import glob
import sqlite3

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
con = sqlite3.connect(db)
cur = con.cursor()
print(f"DB: {db}\n")

NON_TEST = (
    "AND source_file NOT LIKE '%test%' "
    "AND source_file NOT LIKE '%tests%' "
    "AND source_file NOT LIKE '%spec%' "
    "AND source_file NOT LIKE '%fixture%' "
    "AND source_file NOT LIKE '%mock%'"
)
NON_TEST_E = (
    "AND e.source_file NOT LIKE '%test%' "
    "AND e.source_file NOT LIKE '%tests%' "
    "AND e.source_file NOT LIKE '%spec%' "
    "AND e.source_file NOT LIKE '%fixture%' "
    "AND e.source_file NOT LIKE '%mock%'"
)

print("=== Runtime L2 signal counts (distinct src modules) ===")
signals = [
    "applies_guardrail",
    "validated_by_safety_plane",
    "references_policy_hash",
    "execution_terminates_at_uwg",
    "reenters_safety",
    "requires_human_review",
    "records_execution_trace",
    "signs_execution_trace",
]
for sig in signals:
    cur.execute(
        f"SELECT COUNT(DISTINCT e.src_id) FROM edges e JOIN nodes n ON e.src_id=n.id"
        f" WHERE n.layer='L2' AND e.relation_type=? {NON_TEST_E}",
        (sig,),
    )
    print(f"  {sig:<42} = {cur.fetchone()[0]}")

print()
print("=== Runtime L2 total calls (distinct src modules) ===")
cur.execute(
    f"SELECT COUNT(DISTINCT e.src_id) FROM edges e JOIN nodes n ON e.src_id=n.id"
    f" WHERE n.layer='L2' AND e.relation_type='calls' {NON_TEST_E}"
)
print(f"  calls (L2 distinct src) = {cur.fetchone()[0]}")

print()
print("=== L2 source files ===")
cur.execute(
    "SELECT DISTINCT resolved_path FROM nodes WHERE layer='L2'"
    " AND entity_type='Module' AND resolved_path NOT LIKE '%test%'"
    " AND resolved_path NOT LIKE '%__pycache__%'"
    " ORDER BY resolved_path"
)
for (p,) in cur.fetchall():
    print(f"  {p}")

print()
print("=== Existing guardrail edges in L2 (sample) ===")
for sig in ["applies_guardrail", "validated_by_safety_plane", "execution_terminates_at_uwg"]:
    cur.execute(
        f"SELECT e.source_file, e.line_no, e.symbol FROM edges e JOIN nodes n ON e.src_id=n.id"
        f" WHERE n.layer='L2' AND e.relation_type=? {NON_TEST_E}"
        f" ORDER BY e.source_file, e.line_no LIMIT 10",
        (sig,),
    )
    rows = cur.fetchall()
    print(f"\n  {sig} ({len(rows)} edges, capped 10):")
    for r in rows:
        print(f"    {str(r[0])[-65:]:<67} line={r[1]} sym={r[2][:40]}")

print()
print("=== UniversalWriteGateway.py ===")
cur.execute(
    "SELECT e.relation_type, e.line_no, e.symbol FROM edges e JOIN nodes n ON e.src_id=n.id"
    " WHERE n.resolved_path LIKE '%UniversalWriteGateway%'"
    " AND n.entity_type='Module'"
    " ORDER BY e.relation_type, e.line_no"
)
for r in cur.fetchall():
    print(f"  rel={r[0]:<40} line={r[1]} sym={r[2][:50]}")

print()
print("=== Key L2 execution engine files ===")
for fname in [
    "base_exec_engine",
    "execution_orchestrator",
    "brief_assembly_engine",
    "proposal_assembly_engine",
    "UniversalWriteGateway",
]:
    cur.execute(
        "SELECT e.relation_type, COUNT(*) FROM edges e JOIN nodes n ON e.src_id=n.id"
        f" WHERE n.resolved_path LIKE '%{fname}%' AND n.entity_type='Module'"
        " GROUP BY e.relation_type ORDER BY COUNT(*) DESC LIMIT 8"
    )
    rows = cur.fetchall()
    if rows:
        print(f"\n  {fname}:")
        for r in rows:
            print(f"    {r[0]:<40} = {r[1]}")

con.close()
