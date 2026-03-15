"""Find highest-impact files to wire for each P0 gap."""

import glob
import os
import sqlite3

files = glob.glob("artifacts/adg/adg_indexed_*.sqlite")
latest = max(files, key=os.path.getmtime)
conn = sqlite3.connect(latest)
cur = conn.cursor()

# L1/L6: Find runtime files with most 'calls' edges that DON'T have records_execution_trace
print("=== L1/L6 TOP RUNTIME FILES LACKING records_execution_trace ===")
cur.execute("""
    SELECT n.resolved_path, n.layer, COUNT(*) as calls
    FROM edges e JOIN nodes n ON e.src_id = n.id
    WHERE e.relation_type='calls'
      AND n.layer IN ('L1','L2','L3','L_APP','L_SHARED')
      AND n.resolved_path NOT IN (
        SELECT DISTINCT n2.resolved_path FROM edges e2 JOIN nodes n2 ON e2.src_id = n2.id
        WHERE e2.relation_type='records_execution_trace'
      )
    GROUP BY n.resolved_path ORDER BY calls DESC LIMIT 20
""")
for r in cur.fetchall():
    print(f"  {r[1]:10s}  {r[2]:4d}  {r[0]}")

# L2: Find runtime L1/L2/L3 files calling things without applies_guardrail
print("\n=== L2 TOP RUNTIME EXECUTION ENTRY POINTS (no guardrail) ===")
cur.execute("""
    SELECT n.resolved_path, n.layer, COUNT(*) as calls
    FROM edges e JOIN nodes n ON e.src_id = n.id
    WHERE e.relation_type='calls'
      AND n.layer IN ('L2','L3')
      AND n.resolved_path NOT IN (
        SELECT DISTINCT n2.resolved_path FROM edges e2 JOIN nodes n2 ON e2.src_id = n2.id
        WHERE e2.relation_type='applies_guardrail'
      )
    GROUP BY n.resolved_path ORDER BY calls DESC LIMIT 15
""")
for r in cur.fetchall():
    print(f"  {r[1]:10s}  {r[2]:4d}  {r[0]}")

# L3: Find L3 orchestration files that dispatch agents
print("\n=== L3 ORCHESTRATION DISPATCH SITES (run_agent / dispatch / execute) ===")
cur.execute("""
    SELECT DISTINCT n.resolved_path, e.symbol, e.line_no
    FROM edges e JOIN nodes n ON e.src_id = n.id
    WHERE n.layer='L3'
      AND e.relation_type='calls'
      AND (e.symbol LIKE '%run_agent%' OR e.symbol LIKE '%_dispatch%'
           OR e.symbol LIKE '%run_phase%' OR e.symbol LIKE '%execute_agent%'
           OR e.symbol LIKE '%run_mission%' OR e.symbol LIKE '%dispatch_agent%')
    ORDER BY n.resolved_path, e.line_no
    LIMIT 30
""")
for r in cur.fetchall():
    print(f"  {r[0]}:{r[2]}  {r[1]}")

# L4: Find files with most direct writes (writes_to) but no writes_through
print("\n=== L4 TOP write_to FILES LACKING writes_through (runtime) ===")
cur.execute("""
    SELECT n.resolved_path, n.layer, COUNT(*) as cnt
    FROM edges e JOIN nodes n ON e.src_id = n.id
    WHERE e.relation_type='writes_to'
      AND n.layer NOT LIKE 'L_TEST%'
      AND n.layer NOT LIKE 'L_OPS%'
      AND n.resolved_path NOT IN (
        SELECT DISTINCT n2.resolved_path FROM edges e2 JOIN nodes n2 ON e2.src_id = n2.id
        WHERE e2.relation_type='writes_through'
      )
    GROUP BY n.resolved_path ORDER BY cnt DESC LIMIT 20
""")
for r in cur.fetchall():
    print(f"  {r[1]:10s}  {r[2]:4d}  {r[0]}")

# L5: Find runtime files that reads_policy_state but don't applies_guardrail
print("\n=== L5 TOP RUNTIME POLICY READ SITES (no guardrail enforcement) ===")
cur.execute("""
    SELECT n.resolved_path, n.layer, COUNT(*) as cnt
    FROM edges e JOIN nodes n ON e.src_id = n.id
    WHERE e.relation_type='reads_policy_state'
      AND n.layer NOT LIKE 'L_TEST%'
      AND n.resolved_path NOT IN (
        SELECT DISTINCT n2.resolved_path FROM edges e2 JOIN nodes n2 ON e2.src_id = n2.id
        WHERE e2.relation_type='applies_guardrail'
      )
    GROUP BY n.resolved_path ORDER BY cnt DESC LIMIT 20
""")
for r in cur.fetchall():
    print(f"  {r[1]:10s}  {r[2]:4d}  {r[0]}")

conn.close()
