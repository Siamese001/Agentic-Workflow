"""
Query records_execution_trace coverage from ADG SQLite database.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("query_execution_trace_coverage", "query_execution_trace_coverage_digest")
record_execution_trace("query_execution_trace_coverage", "query_execution_trace_coverage_trace")


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

    # Total records_execution_trace edges
    cur.execute('SELECT COUNT(*) FROM edges WHERE relation_type = "records_execution_trace"')
    total_trace_edges = cur.fetchone()[0]
    print(f"Total records_execution_trace edges: {total_trace_edges}")

    # Files with execution trace
    cur.execute(
        'SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type = "records_execution_trace"'
    )
    files_with_trace = cur.fetchone()[0]
    print(f"Files with execution trace: {files_with_trace}")

    # Top 20 files by trace coverage
    cur.execute("""
        SELECT source_file, COUNT(*) as cnt
        FROM edges
        WHERE relation_type = "records_execution_trace"
        GROUP BY source_file
        ORDER BY cnt DESC
        LIMIT 20
    """)
    print("\n=== Top 20 Files by Execution Trace Coverage ===\n")
    for source_file, cnt in cur.fetchall():
        print(f"{source_file}: {cnt} sites")

    # Layer distribution
    cur.execute("""
        SELECT
            CASE
                WHEN source_file LIKE 'agentic_core/L0_%' THEN 'L0'
                WHEN source_file LIKE 'agentic_core/L1_%' THEN 'L1'
                WHEN source_file LIKE 'agentic_core/L2_%' THEN 'L2'
                WHEN source_file LIKE 'agentic_core/L3_%' THEN 'L3'
                WHEN source_file LIKE 'agentic_core/L4_%' THEN 'L4'
                WHEN source_file LIKE 'agentic_core/L5_%' THEN 'L5'
                WHEN source_file LIKE 'agentic_core/L6_%' THEN 'L6'
                WHEN source_file LIKE 'apps_%' THEN 'L_APP'
                WHEN source_file LIKE 'ops_scripts/%' THEN 'L_OPS'
                WHEN source_file LIKE 'tools/%' THEN 'L_TOOLS'
                WHEN source_file LIKE 'tests/%' THEN 'L_TEST'
                ELSE 'OTHER'
            END as layer,
            COUNT(*) as trace_count
        FROM edges
        WHERE relation_type = "records_execution_trace"
        GROUP BY layer
        ORDER BY trace_count DESC
    """)
    print("\n=== Execution Trace Coverage by Layer ===\n")
    for layer, count in cur.fetchall():
        print(f"{layer}: {count} sites")

    # Files WITHOUT execution trace (sample)
    cur.execute("""
        SELECT DISTINCT source_file
        FROM edges
        WHERE source_file NOT IN (
            SELECT DISTINCT source_file
            FROM edges
            WHERE relation_type = "records_execution_trace"
        )
        AND source_file LIKE 'agentic_core/%'
        AND source_file NOT LIKE 'tests/%'
        LIMIT 50
    """)
    print("\n=== Sample Files WITHOUT Execution Trace (agentic_core only) ===\n")
    files_without_trace = cur.fetchall()
    for (source_file,) in files_without_trace[:20]:
        print(f"  {source_file}")
    if len(files_without_trace) > 20:
        print(f"  ... and {len(files_without_trace) - 20} more")

    conn.close()


if __name__ == "__main__":
    main()
