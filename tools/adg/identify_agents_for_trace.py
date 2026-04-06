"""
Identify high-priority agents without execution trace coverage.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("identify_agents_for_trace", "identify_agents_for_trace_digest")
record_execution_trace("identify_agents_for_trace", "identify_agents_for_trace_trace")


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

    # Find Agent classes in L3 and L5 without execution trace
    cur.execute("""
        SELECT DISTINCT n.adg_name, n.resolved_path, n.layer
        FROM nodes n
        WHERE n.entity_type = 'class'
        AND n.adg_name LIKE '%Agent'
        AND n.layer IN ('L3', 'L5')
        AND n.id NOT IN (
            SELECT DISTINCT src_id
            FROM edges
            WHERE relation_type = 'records_execution_trace'
        )
        ORDER BY n.layer, n.adg_name
        LIMIT 30
    """)

    print("=== High-Priority Agents Without Execution Trace ===\n")
    print("L3 (Orchestration) and L5 (Safety) agents:\n")

    agents = cur.fetchall()
    if not agents:
        print("  (All L3/L5 agents already have execution trace)")
    else:
        for agent_name, path, layer in agents:
            print(f"  [{layer}] {agent_name}")
            if path:
                print(f"       {path}")

    print(f"\nTotal agents found: {len(agents)}")

    # Also check L2 execution agents
    cur.execute("""
        SELECT DISTINCT n.adg_name, n.resolved_path
        FROM nodes n
        WHERE n.entity_type = 'class'
        AND n.adg_name LIKE '%Agent'
        AND n.layer = 'L2'
        AND n.id NOT IN (
            SELECT DISTINCT src_id
            FROM edges
            WHERE relation_type = 'records_execution_trace'
        )
        ORDER BY n.adg_name
        LIMIT 10
    """)

    l2_agents = cur.fetchall()
    if l2_agents:
        print("\n=== L2 (Execution) Agents Without Trace ===\n")
        for agent_name, path in l2_agents:
            print(f"  [L2] {agent_name}")
            if path:
                print(f"       {path}")

    conn.close()


if __name__ == "__main__":
    main()
