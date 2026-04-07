"""
Query writes_through coverage from ADG SQLite database.
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

    # Total writes_through edges
    cur.execute('SELECT COUNT(*) FROM edges WHERE relation_type = "writes_through"')
    total_writes = cur.fetchone()[0]
    print(f"Total writes_through edges: {total_writes}")

    # Files with writes_through
    cur.execute('SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type = "writes_through"')
    files_with_writes = cur.fetchone()[0]
    print(f"Files with writes_through: {files_with_writes}")

    # Total state mutation operations (for ratio calculation)
    cur.execute("""
        SELECT COUNT(*) FROM edges
        WHERE relation_type IN ('mutates_state', 'writes_to_db', 'modifies_cache')
    """)
    total_mutations = cur.fetchone()[0]
    print(f"Total state mutation operations: {total_mutations}")

    if total_mutations > 0:
        ratio = (total_writes / total_mutations) * 100
        print(f"Current writes_through ratio: {ratio:.1f}%")

    # Top 20 files by writes_through coverage
    cur.execute("""
        SELECT source_file, COUNT(*) as cnt
        FROM edges
        WHERE relation_type = "writes_through"
        GROUP BY source_file
        ORDER BY cnt DESC
        LIMIT 20
    """)
    print("\n=== Top 20 Files by Writes-Through Coverage ===\n")
    results = cur.fetchall()
    if results:
        for source_file, cnt in results:
            print(f"{source_file}: {cnt} sites")
    else:
        print("  (No writes_through edges found)")

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
            COUNT(*) as write_count
        FROM edges
        WHERE relation_type = "writes_through"
        GROUP BY layer
        ORDER BY write_count DESC
    """)
    print("\n=== Writes-Through Coverage by Layer ===\n")
    layer_results = cur.fetchall()
    if layer_results:
        for layer, count in layer_results:
            print(f"{layer}: {count} sites")
    else:
        print("  (No layer distribution available)")

    conn.close()


if __name__ == "__main__":
    main()
