#!/usr/bin/env python3
"""Deep validation of specific MV findings."""

import sqlite3
from pathlib import Path

adg_dir = Path('artifacts/adg')
sqlite_files = sorted(adg_dir.glob('adg_indexed_*.sqlite'))
sqlite_path = sqlite_files[-1]
conn = sqlite3.connect(str(sqlite_path))
cur = conn.cursor()

# 1. Why is fan_in 0 in mv_hotspot_centrality?
print("=== Finding 1: mv_hotspot_centrality blind to inbound ===")
cur.execute("""SELECT COUNT(*) FROM edges 
    WHERE relation_type IN ('imports', 'calls') 
    AND src_id IS NOT NULL AND dst_id IS NOT NULL""")
total_imports_calls = cur.fetchone()[0]
print(f"Total imports+calls edges: {total_imports_calls}")

# Check raw edge counts by direction
cur.execute("""SELECT 
    COUNT(DISTINCT e.dst_id) as modules_with_inbound,
    COUNT(DISTINCT n.id) as total_modules
    FROM edges e
    JOIN nodes n ON n.id = e.dst_id
    WHERE e.relation_type IN ('imports', 'calls')
    AND n.entity_type = 'module'""")
mi, tm = cur.fetchone()
print(f"Modules with inbound edges: {mi}/{tm}")

# 2. Check mv_snapshot_integrity_anomalies - why 211K rows?
print("\n=== Finding 2: mv_snapshot_integrity_anomalies (211,602 rows) ===")
cur.execute('SELECT COUNT(*), COUNT(DISTINCT node_id) FROM mv_snapshot_integrity_anomalies')
total, distinct = cur.fetchone()
print(f"Total rows: {total}, Distinct nodes: {distinct}")

# Sample the anomaly types
print("\nSample anomalies:")
cur.execute('SELECT DISTINCT anomaly_type, COUNT(*) FROM mv_snapshot_integrity_anomalies GROUP BY anomaly_type LIMIT 10')
for row in cur.fetchall():
    print(f"  {row[0][:50]:50} {row[1]:6}")

# 3. Check mv_exemptions_near_critical_paths - 4439 exemptions
print("\n=== Finding 3: mv_exemptions_near_critical_paths (4,439 rows) ===")
cur.execute('SELECT COUNT(DISTINCT exempt_node_id), COUNT(DISTINCT critical_node_id) FROM mv_exemptions_near_critical_paths')
exempt_count, critical_count = cur.fetchone()
print(f"Exempt modules: {exempt_count}, Near critical modules: {critical_count}")

# 4. Check infra wiring violations
print("\n=== Finding 4: Infra Wiring Views ===")
infra_views = ['v_p0_apps_direct_infra', 'v_p0_provider_bypass', 'v_p0_write_bypass_uwg', 
               'v_p1_zero_caller_infra', 'v_p1_not_on_spine', 'v_p2_mixed_usage']
for view in infra_views:
    try:
        count = cur.execute(f"SELECT COUNT(*) FROM {view}").fetchone()[0]
        print(f"  {view}: {count}")
    except sqlite3.OperationalError:
        print(f"  {view}: MISSING")

# 5. Check SC/AP violations if any
print("\n=== Finding 5: SC/AP Violations ===")
cur.execute("""SELECT file_path, COUNT(*) FROM violations 
    WHERE category LIKE 'SC-%' OR category LIKE 'AP-%'
    GROUP BY file_path 
    ORDER BY COUNT(*) DESC 
    LIMIT 10""")
rows = cur.fetchall()
if rows:
    for row in rows:
        print(f"  {row[0][:50]:50} {row[1]:4}")
else:
    print("  No SC/AP violations found (checks disabled)")

# 6. Check trace/replay gaps
print("\n=== Finding 6: Trace/Replay Coverage Gaps ===")
cur.execute('SELECT COUNT(*), gap_type FROM mv_trace_replay_eval_gaps GROUP BY gap_type ORDER BY COUNT(*) DESC')
for row in cur.fetchall():
    print(f"  {row[1]}: {row[0]}")

# 7. Check if violations edge_id links are broken
print("\n=== Finding 7: Violations Edge ID Integrity ===")
cur.execute('SELECT COUNT(*) FROM violations WHERE edge_id = 0')
zero_edge = cur.fetchone()[0]
cur.execute('SELECT COUNT(*) FROM violations')
total_v = cur.fetchone()[0]
print(f"Violations with edge_id=0: {zero_edge}/{total_v} ({100*zero_edge/total_v:.1f}%)")

# Check edge_id validity
cur.execute('SELECT COUNT(DISTINCT edge_id) FROM violations WHERE edge_id > 0')
distinct_edges = cur.fetchone()[0]
print(f"Distinct non-zero edge IDs in violations: {distinct_edges}")

conn.close()
