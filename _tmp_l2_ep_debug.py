"""Show what's in the 26 entry-point modules and which lack guardrail."""

import glob
import sqlite3

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
con = sqlite3.connect(db)
cur = con.cursor()

NT = (
    " AND e.source_file NOT LIKE '%test%'"
    " AND e.source_file NOT LIKE '%tests%'"
    " AND e.source_file NOT LIKE '%spec%'"
    " AND e.source_file NOT LIKE '%fixture%'"
    " AND e.source_file NOT LIKE '%mock%'"
)

ENTRY_POINT_PATHS = (
    "%/L2_execution/engines/%",
    "%/L2_execution/tools/%",
    "%/L2_execution/reasoning/%",
    "%/L2_execution/scripts/%",
    "%/L2_execution/UniversalWriteGateway%",
    "%/L2_execution/enforcement/capability_chokepoint%",
    "%/L2_execution/enforcement/execution_guardrail_chokepoint%",
    "%/L2_execution/enforcement/sovereign_filesystem_mcp%",
    "%/L2_execution/enforcement/runtime_interceptor%",
)
like_clauses = " OR ".join("n.resolved_path LIKE ?" for _ in ENTRY_POINT_PATHS)

# All entry-point modules with any execution edge
cur.execute(
    f"SELECT DISTINCT n.resolved_path FROM edges e JOIN nodes n ON e.src_id=n.id"
    f" WHERE n.layer='L2' AND ({like_clauses})"
    f" AND e.relation_type IN ('writes_to','records_execution_trace','calls')"
    + NT
    + " ORDER BY n.resolved_path",
    ENTRY_POINT_PATHS,
)
ep_modules = {r[0] for r in cur.fetchall()}
print(f"Entry-point execution modules ({len(ep_modules)}):")
for m in sorted(ep_modules):
    print(f"  {m}")

# Which have applies_guardrail
cur.execute(
    f"SELECT DISTINCT n.resolved_path FROM edges e JOIN nodes n ON e.src_id=n.id"
    f" WHERE n.layer='L2' AND ({like_clauses})"
    f" AND e.relation_type='applies_guardrail'" + NT + " ORDER BY n.resolved_path",
    ENTRY_POINT_PATHS,
)
guarded = {r[0] for r in cur.fetchall()}
print(f"\nGuarded entry-point modules ({len(guarded)}):")
for m in sorted(guarded):
    print(f"  {m}")

# Gap
gap = ep_modules - guarded
print(f"\nUNGUARDED entry-point modules ({len(gap)}):")
for m in sorted(gap):
    print(f"  {m}")

# Which have validated_by_safety_plane
cur.execute(
    f"SELECT DISTINCT n.resolved_path FROM edges e JOIN nodes n ON e.src_id=n.id"
    f" WHERE n.layer='L2' AND ({like_clauses})"
    f" AND e.relation_type='validated_by_safety_plane'" + NT + " ORDER BY n.resolved_path",
    ENTRY_POINT_PATHS,
)
sp = {r[0] for r in cur.fetchall()}
print(f"\nSafety-plane-validated entry-point modules ({len(sp)}):")
for m in sorted(sp):
    print(f"  {m}")

print(f"\nGuarded but NOT safety-plane ({len(guarded - sp)}):")
for m in sorted(guarded - sp):
    print(f"  {m}")

con.close()
