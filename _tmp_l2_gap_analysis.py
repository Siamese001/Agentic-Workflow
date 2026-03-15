"""Identify which L2 runtime modules lack applies_guardrail / validated_by_safety_plane."""

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

# 1. All L2 runtime exec-carrying modules (writes_to or records_execution_trace)
cur.execute(
    "SELECT DISTINCT n.resolved_path FROM edges e JOIN nodes n ON e.src_id=n.id"
    " WHERE n.layer='L2' AND e.relation_type IN ('writes_to','records_execution_trace')"
    + NT
    + " ORDER BY n.resolved_path"
)
exec_modules = {r[0] for r in cur.fetchall()}
print(f"Exec-carrying modules ({len(exec_modules)}):")
for m in sorted(exec_modules):
    print(f"  {m}")

# 2. Which have applies_guardrail
cur.execute(
    "SELECT DISTINCT n.resolved_path FROM edges e JOIN nodes n ON e.src_id=n.id"
    " WHERE n.layer='L2' AND e.relation_type='applies_guardrail'" + NT + " ORDER BY n.resolved_path"
)
guarded = {r[0] for r in cur.fetchall()}
print(f"\nGuarded modules ({len(guarded)}):")
for m in sorted(guarded):
    print(f"  {m}")

# 3. Gap: exec-carrying but NOT guarded
gap = exec_modules - guarded
print(f"\nUNGUARDED exec-carrying modules ({len(gap)}):")
for m in sorted(gap):
    print(f"  {m}")

# 4. validated_by_safety_plane coverage
cur.execute(
    "SELECT DISTINCT n.resolved_path FROM edges e JOIN nodes n ON e.src_id=n.id"
    " WHERE n.layer='L2' AND e.relation_type='validated_by_safety_plane'" + NT + " ORDER BY n.resolved_path"
)
safety_plane = {r[0] for r in cur.fetchall()}
print(f"\nSafety-plane-validated modules ({len(safety_plane)}):")
for m in sorted(safety_plane):
    print(f"  {m}")

# 5. Guarded but not safety-plane
gap_c = guarded - safety_plane
print(f"\nGuarded but NOT safety-plane ({len(gap_c)}):")
for m in sorted(gap_c):
    print(f"  {m}")

# 6. What kinds of writes_to exist (sample)
print("\n=== writes_to module sample (first 20) ===")
cur.execute(
    "SELECT DISTINCT n.resolved_path FROM edges e JOIN nodes n ON e.src_id=n.id"
    " WHERE n.layer='L2' AND e.relation_type='writes_to'" + NT + " ORDER BY n.resolved_path LIMIT 20"
)
for r in cur.fetchall():
    print(f"  {r[0]}")

con.close()
