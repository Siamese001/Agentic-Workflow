#!/usr/bin/env python3
"""Instrumented diagnostic for Prompt 5 proof-and-fix pass."""

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

sqlite_path = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"))[-1]
conn = sqlite3.connect(str(sqlite_path))
cur = conn.cursor()

print("=== DIAGNOSTIC A: Exact Row Counts ===")
views = [
    "mv_graph_reverse_dependency_hotspots",
    "mv_graph_chokepoint_bridges",
    "mv_graph_scc_clusters",
    "mv_graph_critical_path_blast_radius",
]
for v in views:
    cur.execute(f"SELECT COUNT(*) FROM {v}")
    print(f"{v}: {cur.fetchone()[0]}")

print()
print("=== DIAGNOSTIC B: SCC Analysis ===")

print("Stage 1 - Check if 2-hop reachability temp table exists...")
cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='_t_reachability'")
if cur.fetchone()[0] == 0:
    print("  _t_reachability does NOT exist (dropped after phase_e runs)")
    print("  Creating temp table to analyze...")

    cur.execute("""
        CREATE TEMP TABLE _t_reachability AS
        SELECT DISTINCT
            n1.id AS node_a,
            n2.id AS node_b,
            n1.resolved_path AS path_a,
            n2.resolved_path AS path_b
        FROM edges e1
        JOIN edges e2 ON e2.src_id = e1.dst_id
        JOIN nodes n1 ON e1.src_id = n1.id AND n1.entity_type = 'module'
        JOIN nodes n2 ON e2.dst_id = n2.id AND n2.entity_type = 'module'
        WHERE e1.relation_type IN ('imports', 'calls')
          AND e2.relation_type IN ('imports', 'calls')
          AND n1.resolved_path != n2.resolved_path
    """)
    conn.commit()

print("Stage 2 - Count 2-hop reachability rows:")
cur.execute("SELECT COUNT(*) FROM _t_reachability")
reach_count = cur.fetchone()[0]
print(f"  Count: {reach_count}")

print("Stage 3 - Check for mutual reachability (A->B AND B->A):")
if reach_count > 0:
    cur.execute("""
        SELECT COUNT(*) FROM (
            SELECT r1.node_a, r1.node_b
            FROM _t_reachability r1
            JOIN _t_reachability r2 ON r1.node_a = r2.node_b AND r1.node_b = r2.node_a
        )
    """)
    mutual = cur.fetchone()[0]
    print(f"  Mutual reachability pairs: {mutual}")
    if mutual == 0:
        print("  *** ROOT CAUSE: No mutual reachability found - no cycles/SCCs in dependency graph ***")
else:
    print("  No reachability data to check")

print()
print("=== DIAGNOSTIC C: Watchlist Anomaly Typing ===")

from tools.generate.adg_graph_watchlist_builder import ADGGraphWatchlistBuilder

with ADGGraphWatchlistBuilder(sqlite_path) as builder:
    # Get thresholds
    rev_thresh = builder._get_threshold("mv_graph_reverse_dependency_hotspots", "reverse_dependency_score")
    bridge_thresh = builder._get_threshold("mv_graph_chokepoint_bridges", "bridge_score")
    scc_thresh = builder._get_threshold("mv_graph_scc_clusters", "scc_risk_score")
    blast_thresh = builder._get_threshold("mv_graph_critical_path_blast_radius", "weighted_blast_radius")

    print(
        f"Thresholds: rev={rev_thresh:.2f}, bridge={bridge_thresh:.2f}, scc={scc_thresh:.2f}, blast={blast_thresh:.2f}"
    )
    print()

    watchlist = builder.build_graph_watchlist()
    print(f"Total watchlist items: {len(watchlist)}")
    print()

    print("Per-item boolean analysis (first 5):")
    bug_count = 0
    for item in watchlist[:5]:
        high_rev = item.reverse_dep_score >= rev_thresh and item.reverse_dep_score > 0
        high_bridge = item.bridge_score >= bridge_thresh and item.bridge_score > 0
        high_scc = item.scc_cluster_size >= scc_thresh and item.scc_cluster_size > 0
        high_blast = item.blast_radius >= blast_thresh and item.blast_radius > 0

        signals = []
        if high_rev:
            signals.append("rev")
        if high_bridge:
            signals.append("bridge")
        if high_scc:
            signals.append("scc")
        if high_blast:
            signals.append("blast")

        is_bug = "multi" in item.graph_anomaly_type and len(signals) < 2
        if is_bug:
            bug_count += 1

        print(f"  {item.rank}. {item.file[:50]}")
        print(
            f"     Raw: rev={item.reverse_dep_score:.2f}, bridge={item.bridge_score:.2f}, scc={item.scc_cluster_size}, blast={item.blast_radius:.2f}"
        )
        print(f"     Booleans: rev={high_rev}, bridge={high_bridge}, scc={high_scc}, blast={high_blast}")
        print(f"     Signals list: {signals} (count={len(signals)})")
        print(f"     Type assigned: {item.graph_anomaly_type}")
        if is_bug:
            print(f"     *** BUG CONFIRMED: multi_signal type but only {len(signals)} signals ***")
        print()

    if bug_count > 0:
        print(f"TOTAL BUGS: {bug_count} items misclassified as multi_signal")

print()
print("=== DIAGNOSTIC D: Scoring Math ===")
if watchlist:
    print("Score composition (first 3 items):")
    for item in watchlist[:3]:
        rev_w = min(item.reverse_dep_score / 100 * 25, 25)
        bridge_w = min(item.bridge_score / 50 * 20, 20)
        scc_w = min(item.scc_cluster_size / 100 * 20, 20)
        blast_w = min(item.blast_radius / 100 * 25, 25)
        base_total = rev_w + bridge_w + scc_w + blast_w
        layer_mult = (
            1.25
            if item.layer in {"L0", "L1", "L2", "L3", "L4", "L5", "L6", "L_APP", "L_SHARED", "L_RUNTIME"}
            else 1.0
        )
        computed = base_total * layer_mult

        print(f"{item.rank}. {item.file[:40]}")
        print(
            f"   Weights: rev={rev_w:.2f} + bridge={bridge_w:.2f} + scc={scc_w:.2f} + blast={blast_w:.2f} = {base_total:.2f}"
        )
        print(f"   Multiplier: {layer_mult}")
        print(f"   Computed: {computed:.2f}, Stored: {item.score}, Match: {abs(computed - item.score) < 0.1}")
        print()

    print("NOTE: Base weights total 90 (25+20+20+25), not 100. This is acceptable with caps.")

conn.close()
print()
print("=== END DIAGNOSTICS ===")
