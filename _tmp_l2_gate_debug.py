"""L2 gate debug — diagnose Gate A/C/D failures."""

import glob
import sqlite3

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
con = sqlite3.connect(db)
cur = con.cursor()
print(f"DB: {db}\n")

NT = (
    " AND e.source_file NOT LIKE '%test%'"
    " AND e.source_file NOT LIKE '%tests%'"
    " AND e.source_file NOT LIKE '%spec%'"
    " AND e.source_file NOT LIKE '%fixture%'"
    " AND e.source_file NOT LIKE '%mock%'"
)

# 1. reenters_safety — what edges exist
print("=== reenters_safety edges (all layers) ===")
cur.execute(
    "SELECT e.relation_type, e.source_file, e.line_no, e.symbol FROM edges e"
    " WHERE e.relation_type='reenters_safety' LIMIT 10"
)
for r in cur.fetchall():
    print(f"  {r[0]:<30} {str(r[1])[-50:]:<52} line={r[2]} sym={r[3][:40]}")

# 2. What _emit_reenters_safety maps to
print("\n=== _emit_reenters_safety symbol edges ===")
cur.execute(
    "SELECT e.relation_type, e.source_file, e.line_no FROM edges WHERE symbol LIKE '%reenters_safety%'"
)
for r in cur.fetchall():
    print(f"  rel={r[0]:<35} {str(r[1])[-50:]:<52} line={r[2]}")

# 3. escalates_to_human / similar
print("\n=== escalation-type edge totals ===")
for sig in ["escalates_to_human", "reenters_safety", "requires_human_review"]:
    cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (sig,))
    print(f"  {sig}: {cur.fetchone()[0]}")

# 4. execution_guardrail_chokepoint all edges
print("\n=== execution_guardrail_chokepoint module edges ===")
cur.execute(
    "SELECT e.relation_type, e.line_no, e.symbol FROM edges e JOIN nodes n ON e.src_id=n.id"
    " WHERE n.resolved_path LIKE '%execution_guardrail_chokepoint%'"
    " AND n.entity_type='Module'"
    " ORDER BY e.relation_type, e.line_no"
)
for r in cur.fetchall():
    print(f"  {r[0]:<40} line={r[1]} sym={r[2][:50]}")

# 5. Gate A denominator — what are the 74 L2 call modules?
print("\n=== L2 distinct call modules (runtime, all) ===")
cur.execute(
    "SELECT DISTINCT n.resolved_path FROM edges e JOIN nodes n ON e.src_id=n.id"
    " WHERE n.layer='L2' AND e.relation_type='calls'" + NT + " ORDER BY n.resolved_path"
)
rows = cur.fetchall()
print(f"  Total: {len(rows)}")
for r in rows:
    print(f"  {r[0]}")

# 6. What scanner visitor handles reenters_safety
print("\n=== edges with relation_type containing 'reenter' ===")
cur.execute("SELECT DISTINCT relation_type FROM edges WHERE relation_type LIKE '%reenter%'")
for r in cur.fetchall():
    print(f"  {r[0]}")

# 7. action_node / execution_gateway edges
print("\n=== action_node / execution_gateway guardrail edges ===")
for fname in ["action_node", "execution_gateway", "execution_guardrail"]:
    cur.execute(
        "SELECT e.relation_type, e.line_no, e.symbol FROM edges e JOIN nodes n ON e.src_id=n.id"
        f" WHERE n.resolved_path LIKE '%{fname}%' AND n.entity_type='Module'"
        " AND e.relation_type IN ('applies_guardrail','validated_by_safety_plane',"
        "  'references_policy_hash','reenters_safety','requires_human_review',"
        "  'execution_terminates_at_uwg','records_execution_trace','signs_execution_trace')"
        " ORDER BY e.relation_type, e.line_no"
    )
    rows = cur.fetchall()
    print(f"\n  {fname} ({len(rows)} signal edges):")
    for r in rows:
        print(f"    {r[0]:<42} line={r[1]} sym={r[2][:40]}")

con.close()
