"""Audit all P0 gap signals from the latest ADG SQLite."""

import glob
import os
import sqlite3

files = glob.glob("artifacts/adg/adg_indexed_*.sqlite")
latest = max(files, key=os.path.getmtime)
print("Using:", latest)
conn = sqlite3.connect(latest)
cur = conn.cursor()

signals = [
    "records_execution_trace",
    "signs_execution_trace",
    "applies_guardrail",
    "agent_executes_agent",
    "reads_runtime_state",
    "observes_runtime_state",
    "snapshots_state",
    "writes_through",
    "reads_policy_state",
    "references_policy_hash",
    "validated_by_safety_plane",
    "emits_replay_key",
    "emits_determinism_digest",
]

print("\n=== ALL SIGNAL COUNTS (runtime vs test) ===")
for sig in signals:
    cur.execute(
        """
        SELECT
            SUM(CASE WHEN n.layer NOT LIKE 'L_TEST%' THEN 1 ELSE 0 END) as runtime,
            SUM(CASE WHEN n.layer LIKE 'L_TEST%' THEN 1 ELSE 0 END) as test,
            COUNT(*) as total
        FROM edges e
        JOIN nodes n ON e.src_id = n.id
        WHERE e.relation_type=?
    """,
        (sig,),
    )
    row = cur.fetchone()
    print(f"  {sig:40s}  runtime={row[0] or 0:4d}  test={row[1] or 0:4d}  total={row[2] or 0:4d}")

print("\n=== RUNTIME RECORDS_EXECUTION_TRACE sources ===")
cur.execute("""
    SELECT n.resolved_path, n.layer, e.symbol, e.line_no
    FROM edges e JOIN nodes n ON e.src_id = n.id
    WHERE e.relation_type='records_execution_trace'
      AND n.layer NOT LIKE 'L_TEST%'
    ORDER BY n.layer, n.resolved_path
""")
for row in cur.fetchall():
    print(f"  {row[1]:8s}  {row[0]}:{row[3]}  {row[2]}")

print("\n=== RUNTIME APPLIES_GUARDRAIL sources ===")
cur.execute("""
    SELECT n.resolved_path, n.layer, e.symbol, e.line_no
    FROM edges e JOIN nodes n ON e.src_id = n.id
    WHERE e.relation_type='applies_guardrail'
      AND n.layer NOT LIKE 'L_TEST%'
    ORDER BY n.layer, n.resolved_path
""")
for row in cur.fetchall():
    print(f"  {row[1]:8s}  {row[0]}:{row[3]}  {row[2]}")

print("\n=== RUNTIME AGENT_EXECUTES_AGENT sources ===")
cur.execute("""
    SELECT n.resolved_path, n.layer, e.symbol, e.line_no
    FROM edges e JOIN nodes n ON e.src_id = n.id
    WHERE e.relation_type='agent_executes_agent'
    ORDER BY n.layer, n.resolved_path
""")
for row in cur.fetchall():
    print(f"  {row[1]:8s}  {row[0]}:{row[3]}  {row[2]}")

print("\n=== TOP RUNTIME CALLERS (no trace) by layer ===")
cur.execute("""
    SELECT n.layer, COUNT(*) as cnt
    FROM edges e JOIN nodes n ON e.src_id = n.id
    WHERE e.relation_type='calls'
      AND n.layer NOT LIKE 'L_TEST%'
    GROUP BY n.layer ORDER BY cnt DESC LIMIT 10
""")
for row in cur.fetchall():
    print(f"  {row[0]:15s}  {row[1]:5d}")

print("\n=== RUNTIME WRITES_THROUGH sources (top files) ===")
cur.execute("""
    SELECT n.resolved_path, COUNT(*) as cnt
    FROM edges e JOIN nodes n ON e.src_id = n.id
    WHERE e.relation_type='writes_through'
      AND n.layer NOT LIKE 'L_TEST%'
    GROUP BY n.resolved_path ORDER BY cnt DESC LIMIT 15
""")
for row in cur.fetchall():
    print(f"  {row[1]:4d}  {row[0]}")

print("\n=== RUNTIME EMITS_REPLAY_KEY sources ===")
cur.execute("""
    SELECT n.resolved_path, n.layer, e.symbol, e.line_no
    FROM edges e JOIN nodes n ON e.src_id = n.id
    WHERE e.relation_type='emits_replay_key'
      AND n.layer NOT LIKE 'L_TEST%'
    ORDER BY n.layer, n.resolved_path
""")
for row in cur.fetchall():
    print(f"  {row[1]:8s}  {row[0]}:{row[3]}  {row[2]}")

conn.close()
