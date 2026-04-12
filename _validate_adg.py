#!/usr/bin/env python3
"""Validate ADG materialized views and findings."""

import sqlite3
import json
from pathlib import Path

# Find latest SQLite
adg_dir = Path("artifacts/adg")
sqlite_files = sorted(adg_dir.glob("adg_indexed_*.sqlite"))
if not sqlite_files:
    print("No SQLite found")
    exit(1)
sqlite_path = sqlite_files[-1]
print(f"Using: {sqlite_path.name}")

conn = sqlite3.connect(str(sqlite_path))
cur = conn.cursor()

# Check which materialized views exist
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'mv_%'")
mv_tables = [r[0] for r in cur.fetchall()]
print(f"\nMaterialized views found: {len(mv_tables)}")
for t in mv_tables:
    count = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"  {t}: {count} rows")

# Check if hotspot centrality has meaningful data
if "mv_hotspot_centrality" in mv_tables:
    print("\n--- mv_hotspot_centrality analysis ---")
    cur.execute(
        "SELECT COUNT(*), AVG(fan_in), MAX(fan_in), AVG(fan_out), MAX(fan_out) FROM mv_hotspot_centrality"
    )
    total, avg_fi, max_fi, avg_fo, max_fo = cur.fetchone()
    print(f"Total modules: {total}")
    print(f"Fan-in: avg={avg_fi:.1f}, max={max_fi}")
    print(f"Fan-out: avg={avg_fo:.1f}, max={max_fo}")

    # Top 10 by fan-in with their layers
    cur.execute(
        "SELECT resolved_path, layer, fan_in, fan_out FROM mv_hotspot_centrality ORDER BY fan_in DESC LIMIT 10"
    )
    print("\nTop 10 by fan-in:")
    for row in cur.fetchall():
        print(f"  {row[1] or 'N/A':8} fi={row[2]:4} fo={row[3]:4} {row[0][:60]}")

# Check dependency cone risk
if "mv_dependency_cone_risk" in mv_tables:
    print("\n--- mv_dependency_cone_risk analysis ---")
    cur.execute("SELECT COUNT(*), AVG(cone_risk_score), MAX(cone_risk_score) FROM mv_dependency_cone_risk")
    total, avg_score, max_score = cur.fetchone()
    print(f"Total modules: {total}")
    print(f"Cone risk: avg={avg_score:.2f}, max={max_score}")

    # Check hop distribution
    cur.execute(
        "SELECT COUNT(*), AVG(hop2_fan_in), MAX(hop2_fan_in) FROM mv_dependency_cone_risk WHERE hop2_fan_in > 0"
    )
    h2_count, h2_avg, h2_max = cur.fetchone()
    h2_count = h2_count or 0
    h2_avg = h2_avg or 0
    print(f"\nModules with hop-2 fan-in: {h2_count} ({100 * h2_count / total:.1f}%)")
    print(f"Hop-2 fan-in: avg={h2_avg:.1f}, max={h2_max}")

    # Top 10 highest cone risk
    cur.execute(
        "SELECT resolved_path, layer, direct_fan_in, hop2_fan_in, cone_risk_score FROM mv_dependency_cone_risk ORDER BY cone_risk_score DESC LIMIT 10"
    )
    print("\nTop 10 cone risk:")
    for row in cur.fetchall():
        print(f"  {row[1] or 'N/A':8} d={row[2]:4} h2={row[3]:4} score={row[4]:.2f} {row[0][:50]}")

# Check runtime spine gaps
if "mv_runtime_spine_gaps" in mv_tables:
    print("\n--- mv_runtime_spine_gaps analysis ---")
    cur.execute(
        "SELECT layer, module_count, gap_count, gap_pct FROM mv_runtime_spine_gaps ORDER BY gap_count DESC"
    )
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} modules, {row[2]} gaps ({row[3]:.1f}%)")

# Check violations table
print("\n--- violations table ---")
cur.execute("SELECT COUNT(*) FROM violations")
v_total = cur.fetchone()[0]
print(f"Total violations: {v_total}")

if v_total > 0:
    cur.execute(
        "SELECT severity, category, COUNT(*) FROM violations GROUP BY severity, category ORDER BY severity, category"
    )
    print("By severity/category:")
    for row in cur.fetchall():
        print(f"  {row[0]:8} {row[1]:20} {row[2]}")

# Check antipattern edges
cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type='antipattern'")
antipattern_count = cur.fetchone()[0]
print(f"\nAntipattern edges: {antipattern_count}")

# Check trace/replay coverage
cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type='records_execution_trace'")
trace_count = cur.fetchone()[0]
print(f"Trace edges: {trace_count}")

cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type='snapshots_state'")
snapshot_count = cur.fetchone()[0]
print(f"Snapshot edges: {snapshot_count}")

# Check cross-layer edges
cur.execute("""SELECT COUNT(*) FROM edges e
    JOIN nodes src ON e.src_id = src.id
    JOIN nodes dst ON e.dst_id = dst.id
    WHERE src.layer IS NOT NULL AND dst.layer IS NOT NULL AND src.layer != dst.layer""")
cross_layer = cur.fetchone()[0]
print(f"\nCross-layer edges: {cross_layer}")

# Check for violations on high fan-in modules
print("\n--- High-risk hotspot violations ---")
if "mv_hotspot_centrality" in mv_tables and v_total > 0:
    cur.execute("""SELECT hc.resolved_path, hc.layer, hc.fan_in, hc.fan_out, COUNT(v.id) as vcount
        FROM mv_hotspot_centrality hc
        JOIN edges e ON e.src_id = hc.node_id
        JOIN violations v ON v.edge_id = e.id
        WHERE hc.fan_in > 50
        GROUP BY hc.node_id
        ORDER BY vcount DESC
        LIMIT 10""")
    rows = cur.fetchall()
    if rows:
        print("Top hotspot-violation correlations:")
        for row in rows:
            print(f"  {row[1] or 'N/A':8} fi={row[2]:4} v={row[4]:3} {row[0][:50]}")
    else:
        print("No violations on high fan-in modules (may be empty edge_id mapping)")

conn.close()
print("\n=== Validation complete ===")
