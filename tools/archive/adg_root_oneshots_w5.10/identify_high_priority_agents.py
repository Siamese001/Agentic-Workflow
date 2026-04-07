"""
Identify high-priority agents for execution trace instrumentation.
Focus on agents that would provide the most coverage impact.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    adg_dir = ROOT / "artifacts" / "adg"
    sqlite_files = list(adg_dir.glob("adg_indexed_*.sqlite"))
    if not sqlite_files:
        print("No ADG SQLite files found")
        return

    latest_sqlite = max(sqlite_files, key=lambda p: p.stat().st_mtime)
    print(f"Querying: {latest_sqlite.name}\n")

    conn = sqlite3.connect(latest_sqlite)
    cur = conn.cursor()

    # Find ALL agent classes (not just those with trace)
    cur.execute("""
        SELECT DISTINCT n.adg_name, n.resolved_path, n.layer,
               CASE WHEN e.src_id IS NOT NULL THEN 'HAS_TRACE' ELSE 'NO_TRACE' END as trace_status
        FROM nodes n
        LEFT JOIN edges e ON n.id = e.src_id AND e.relation_type = 'records_execution_trace'
        WHERE n.entity_type = 'class'
        AND n.adg_name LIKE '%Agent'
        AND n.layer IN ('L2', 'L3', 'L5')
        ORDER BY n.layer, n.adg_name
        LIMIT 50
    """)

    print("=== All Agents by Layer (with trace status) ===\n")

    agents = cur.fetchall()
    if not agents:
        print("  (No agents found)")
    else:
        for agent_name, path, layer, trace_status in agents:
            status_icon = "✅" if trace_status == "HAS_TRACE" else "❌"
            print(f"  [{layer}] {status_icon} {agent_name}")
            if path:
                print(f"       {path}")

    # Count by layer and trace status
    cur.execute("""
        SELECT n.layer,
               CASE WHEN e.src_id IS NOT NULL THEN 'HAS_TRACE' ELSE 'NO_TRACE' END as trace_status,
               COUNT(*) as count
        FROM nodes n
        LEFT JOIN edges e ON n.id = e.src_id AND e.relation_type = 'records_execution_trace'
        WHERE n.entity_type = 'class'
        AND n.adg_name LIKE '%Agent'
        AND n.layer IN ('L2', 'L3', 'L5')
        GROUP BY n.layer, trace_status
        ORDER BY n.layer, trace_status
    """)

    print("\n=== Agent Count by Layer and Trace Status ===\n")
    for layer, trace_status, count in cur.fetchall():
        status_icon = "✅" if trace_status == "HAS_TRACE" else "❌"
        print(f"  [{layer}] {status_icon} {trace_status}: {count} agents")

    # Files without trace that contain agent classes
    cur.execute("""
        SELECT DISTINCT n.resolved_path, n.layer, n.adg_name
        FROM nodes n
        WHERE n.entity_type = 'class'
        AND n.adg_name LIKE '%Agent'
        AND n.layer IN ('L2', 'L3', 'L5')
        AND n.id NOT IN (
            SELECT DISTINCT src_id
            FROM edges
            WHERE relation_type = 'records_execution_trace'
        )
        ORDER BY n.layer, n.resolved_path
        LIMIT 20
    """)

    print("\n=== Files with Agents Lacking Execution Trace ===\n")
    files_without_trace = cur.fetchall()
    if not files_without_trace:
        print("  (All agent files already have execution trace)")
    else:
        for path, layer, agent_name in files_without_trace:
            print(f"  [{layer}] {path}")
            print(f"         Agent: {agent_name}")

    conn.close()


if __name__ == "__main__":
    main()
