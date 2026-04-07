"""
Find agent files that lack execution trace coverage.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("find_agents_without_trace", "find_agents_without_trace_digest")
record_execution_trace("find_agents_without_trace", "find_agents_without_trace_trace")


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

    # Find files with agent classes but no execution trace
    cur.execute("""
        SELECT DISTINCT n.resolved_path, n.layer,
               GROUP_CONCAT(DISTINCT n.adg_name, ', ') as agents
        FROM nodes n
        WHERE n.entity_type = 'class'
        AND n.adg_name LIKE '%Agent'
        AND n.layer IN ('L2', 'L3', 'L5')
        AND n.id NOT IN (
            SELECT DISTINCT src_id
            FROM edges
            WHERE relation_type = 'records_execution_trace'
        )
        GROUP BY n.resolved_path, n.layer
        ORDER BY n.layer, n.resolved_path
    """)

    results = cur.fetchall()

    if not results:
        print("✅ All agent files already have execution trace coverage")
        return

    print("=== Agent Files Without Execution Trace ===\n")

    for path, layer, agents in results:
        print(f"[{layer}] {path}")
        print(f"       Agents: {agents}")
        print()

    print(f"Total files needing instrumentation: {len(results)}")

    # Create a list of file paths for the instrumentation tool
    print("\n=== File Paths for Instrumentation ===\n")
    file_paths = []
    for path, layer, agents in results:
        full_path = ROOT / path
        if full_path.exists():
            file_paths.append(str(full_path))
            print(str(full_path))

    # Save file paths to a temp file for easy use
    if file_paths:
        temp_file = ROOT / "tools" / "adg" / "agent_files_to_trace.txt"
        temp_file.write_text("\n".join(file_paths))
        print(f"\nSaved {len(file_paths)} file paths to: {temp_file}")

    conn.close()


if __name__ == "__main__":
    main()
