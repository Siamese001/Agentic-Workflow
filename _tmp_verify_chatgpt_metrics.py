#!/usr/bin/env python3
"""Verify ChatGPT's P0-P4 metric analysis against actual ADG data."""

import sqlite3
from pathlib import Path

ADG_PATH = Path("artifacts/adg/adg_indexed_03162026_0702.sqlite")

def main():
    conn = sqlite3.connect(ADG_PATH)
    cursor = conn.cursor()
    
    # Get top 50 relation types by count
    print("=" * 80)
    print("TOP 50 RELATION TYPES IN CURRENT ADG")
    print("=" * 80)
    cursor.execute("""
        SELECT r.name, COUNT(*) as cnt
        FROM edges e
        JOIN relation_types r ON e.relation_type = r.id
        GROUP BY r.name
        ORDER BY cnt DESC
        LIMIT 50
    """)
    
    for name, count in cursor.fetchall():
        print(f"{name:45s} {count:>8,}")
    
    # Get totals
    cursor.execute("SELECT COUNT(*) FROM edges")
    total_edges = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM nodes")
    total_nodes = cursor.fetchone()[0]
    
    print("\n" + "=" * 80)
    print(f"{'TOTAL EDGES':45s} {total_edges:>8,}")
    print(f"{'TOTAL NODES':45s} {total_nodes:>8,}")
    print("=" * 80)
    
    # Check specific metrics ChatGPT mentioned
    print("\n" + "=" * 80)
    print("CHATGPT'S CLAIMED METRICS VERIFICATION")
    print("=" * 80)
    
    chatgpt_claims = {
        'records_execution_trace': 20_833,
        'pulls_context': 5_680,
        'execution_terminates_at_uwg': 5_709,
        'dispatches_healing_run': None,  # Part of sum
        'orchestrates_healing': None,  # Part of sum
        'snapshots_state': 3_020,
        'applies_guardrail': 3_139,
        'invokes_eval': 3_367,
        'proposal_commits_routing': 2_873,
        'writes_through': 5_770,
        'validated_by_safety_plane': 2_903,
        'signs_execution_trace': 3_148,
        'reads_runtime_state': 9_104,
        'reads_env': 6_555,
    }
    
    for metric, claimed in chatgpt_claims.items():
        if claimed is None:
            continue
        cursor.execute("""
            SELECT COUNT(*)
            FROM edges e
            JOIN relation_types r ON e.relation_type = r.id
            WHERE r.name = ?
        """, (metric,))
        actual = cursor.fetchone()[0]
        match = "✅" if actual == claimed else "❌"
        print(f"{match} {metric:45s} ChatGPT: {claimed:>8,}  Actual: {actual:>8,}")
    
    conn.close()

if __name__ == "__main__":
    main()
