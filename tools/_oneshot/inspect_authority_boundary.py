"""Investigate the 17 (or 612 total) authority_boundary violations.

The Notion P1 row references `2_authority_boundary P0 17 cross-layer authority breaches`.
Plan W2.1: focus on `agentic_core/L6_observability/__init__.py` re-exports.
"""

import sqlite3
from pathlib import Path

snap = sorted(p for p in Path("artifacts/adg").glob("adg_indexed_*.sqlite") if "99999999" not in p.name)[-1]
print(f"Snapshot: {snap.name}\n")
con = sqlite3.connect(snap)
cur = con.cursor()

# Find the gate self-consistency row(s)
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%authority%' OR name LIKE '%gate_self%'")
print("Tables matching authority/gate_self:")
for r in cur.fetchall():
    print(f"  {r[0]}")

# Inspect gate_self_consistency
print("\ngate_self_consistency cols:")
cur.execute("PRAGMA table_info(gate_self_consistency)")
for r in cur.fetchall():
    print(f"  {r[1]} {r[2]}")

print("\ngate_self_consistency rows for authority_boundary:")
cur.execute("SELECT * FROM gate_self_consistency WHERE gate_file LIKE '%authority%' OR gate_file LIKE '%boundary%' LIMIT 5")
for r in cur.fetchall():
    print(f"  {r}")

# Look for cross-layer L6->L0 patterns directly
print("\n=== L6 -> lower-layer imports (illegal direction) ===")
cur.execute("""
    SELECT e.source_file, COUNT(*) as cnt
    FROM edges e
    JOIN nodes nd ON nd.id = e.dst_id
    WHERE e.relation_type = 'imports'
      AND e.source_file LIKE 'agentic_core/L6_observability/%'
      AND (nd.resolved_path LIKE 'agentic_core/L0_routing/%'
           OR nd.resolved_path LIKE 'agentic_core/L1_cognition/%'
           OR nd.resolved_path LIKE 'agentic_core/L2_execution/%'
           OR nd.resolved_path LIKE 'agentic_core/L3_orchestration/%'
           OR nd.resolved_path LIKE 'agentic_core/L4_state/%'
           OR nd.resolved_path LIKE 'agentic_core/L5_safety/%')
    GROUP BY 1 ORDER BY 2 DESC LIMIT 20
""")
results = cur.fetchall()
for r in results:
    print(f"  {r[1]:>4}  {r[0]}")
print(f"  Total files: {len(results)}, total imports: {sum(r[1] for r in results)}")

print("\n=== Top L6 -> lower-layer destinations ===")
cur.execute("""
    SELECT nd.resolved_path, COUNT(*) as cnt
    FROM edges e
    JOIN nodes nd ON nd.id = e.dst_id
    WHERE e.relation_type = 'imports'
      AND e.source_file LIKE 'agentic_core/L6_observability/%'
      AND nd.resolved_path LIKE 'agentic_core/L%'
      AND nd.resolved_path NOT LIKE 'agentic_core/L6_observability/%'
    GROUP BY 1 ORDER BY 2 DESC LIMIT 20
""")
for r in cur.fetchall():
    print(f"  {r[1]:>4}  {r[0]}")

# Check materialized view if it exists
print("\n=== mv_actionable_surface_without_schema sample (just to see) ===")
cur.execute("SELECT name FROM sqlite_master WHERE type='view' OR (type='table' AND name LIKE 'mv_%')")
for r in cur.fetchall()[:5]:
    print(f"  view/MV: {r[0]}")

# Specifically list what __init__.py imports from lower layers
print("\n=== L6_observability/__init__.py imports from lower layers ===")
cur.execute("""
    SELECT nd.resolved_path, e.line_no, e.symbol
    FROM edges e
    JOIN nodes nd ON nd.id = e.dst_id
    WHERE e.relation_type = 'imports'
      AND e.source_file = 'agentic_core/L6_observability/__init__.py'
      AND (nd.resolved_path LIKE 'agentic_core/L0_routing/%'
           OR nd.resolved_path LIKE 'agentic_core/L1_cognition/%'
           OR nd.resolved_path LIKE 'agentic_core/L2_execution/%'
           OR nd.resolved_path LIKE 'agentic_core/L3_orchestration/%'
           OR nd.resolved_path LIKE 'agentic_core/L4_state/%'
           OR nd.resolved_path LIKE 'agentic_core/L5_safety/%')
    ORDER BY e.line_no
""")
init_results = cur.fetchall()
for r in init_results:
    print(f"  L{r[1]:>4}: {r[0]} ({r[2]})")
print(f"  TOTAL in __init__.py: {len(init_results)}")
