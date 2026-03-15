"""Find the canonical infrastructure modules for each P0 signal."""

import glob
import os
import sqlite3

files = glob.glob("artifacts/adg/adg_indexed_*.sqlite")
latest = max(files, key=os.path.getmtime)
conn = sqlite3.connect(latest)
cur = conn.cursor()

# Find what functions/classes emit each signal
print("=== WHAT EMITS records_execution_trace (existing patterns) ===")
cur.execute("""
    SELECT DISTINCT e.symbol, n.resolved_path, e.line_no
    FROM edges e JOIN nodes n ON e.src_id = n.id
    WHERE e.relation_type='records_execution_trace'
    ORDER BY n.resolved_path
    LIMIT 20
""")
for r in cur.fetchall():
    print(f"  {r[0]:50s}  {r[1]}:{r[2]}")

print("\n=== WHAT EMITS signs_execution_trace (existing patterns) ===")
cur.execute("""
    SELECT DISTINCT e.symbol, n.resolved_path, e.line_no
    FROM edges e JOIN nodes n ON e.src_id = n.id
    WHERE e.relation_type='signs_execution_trace'
    ORDER BY n.resolved_path
    LIMIT 20
""")
for r in cur.fetchall():
    print(f"  {r[0]:50s}  {r[1]}:{r[2]}")

print("\n=== WHAT EMITS applies_guardrail (key pattern) ===")
cur.execute("""
    SELECT DISTINCT e.symbol, n.resolved_path, e.line_no
    FROM edges e JOIN nodes n ON e.src_id = n.id
    WHERE e.relation_type='applies_guardrail'
      AND n.layer NOT LIKE 'L_TEST%'
    ORDER BY n.resolved_path
    LIMIT 10
""")
for r in cur.fetchall():
    print(f"  {r[0]:50s}  {r[1]}:{r[2]}")

print("\n=== WHAT EMITS validated_by_safety_plane (test patterns) ===")
cur.execute("""
    SELECT DISTINCT e.symbol, n.resolved_path, e.line_no
    FROM edges e JOIN nodes n ON e.src_id = n.id
    WHERE e.relation_type='validated_by_safety_plane'
    ORDER BY n.resolved_path
    LIMIT 10
""")
for r in cur.fetchall():
    print(f"  {r[0]:50s}  {r[1]}:{r[2]}")

print("\n=== TOP L3 nodes by calls (potential agent_executes_agent sites) ===")
cur.execute("""
    SELECT DISTINCT n.resolved_path, e.symbol, e.line_no
    FROM edges e JOIN nodes n ON e.src_id = n.id
    WHERE e.relation_type='calls'
      AND n.layer='L3'
      AND (e.symbol LIKE '%run_agent%' OR e.symbol LIKE '%execute_agent%'
           OR e.symbol LIKE '%dispatch%' OR e.symbol LIKE '%invoke%'
           OR e.symbol LIKE '%orchestrat%')
    ORDER BY n.resolved_path, e.line_no
    LIMIT 30
""")
for r in cur.fetchall():
    print(f"  {r[0]}:{r[2]}  {r[1]}")

print("\n=== WRITES_THROUGH targets ===")
cur.execute("""
    SELECT DISTINCT dst.resolved_path, dst.layer
    FROM edges e
    JOIN nodes src ON e.src_id = src.id
    JOIN nodes dst ON e.dst_id = dst.id
    WHERE e.relation_type='writes_through'
    LIMIT 10
""")
for r in cur.fetchall():
    print(f"  {r[1]:10s}  {r[0]}")

print("\n=== UNIVERSALWRITEGATEWAY usage ===")
cur.execute("""
    SELECT n.resolved_path, e.symbol, e.line_no
    FROM edges e JOIN nodes n ON e.src_id = n.id
    WHERE e.relation_type='imports'
      AND (e.symbol LIKE '%UniversalWrite%' OR e.symbol LIKE '%universal_write%')
    ORDER BY n.resolved_path
    LIMIT 20
""")
for r in cur.fetchall():
    print(f"  {r[0]}:{r[2]}  {r[1]}")

conn.close()
