"""
Detailed analysis of writes_through coverage for Wave 6.
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

    # Basic counts
    cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type = 'writes_through'")
    total_edges = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(DISTINCT source_file)
        FROM edges
        WHERE relation_type = 'writes_through'
        AND source_file LIKE 'agentic_core/%'
    """)
    prod_files = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(DISTINCT source_file)
        FROM edges
        WHERE relation_type = 'writes_through'
        AND source_file LIKE 'test_%'
    """)
    test_files = cur.fetchone()[0]

    print("=== Wave 6: Write-Through Coverage ===\n")
    print(f"Total writes_through edges: {total_edges}")
    print(f"Production files: {prod_files}")
    print(f"Test files: {test_files}")
    print(f"Total files: {prod_files + test_files}\n")

    # Top files by writes_through
    cur.execute("""
        SELECT source_file, COUNT(*) as count
        FROM edges
        WHERE relation_type = 'writes_through'
        AND source_file LIKE 'agentic_core/%'
        GROUP BY source_file
        ORDER BY count DESC
        LIMIT 10
    """)

    print("=== Top Production Files by Write-Through ===\n")
    for file, count in cur.fetchall():
        print(f"  {count:3d} {file}")

    # Layer distribution
    cur.execute("""
        SELECT n.layer, COUNT(e.id) as count
        FROM edges e
        JOIN nodes n ON e.src_id = n.id
        WHERE e.relation_type = 'writes_through'
        AND n.layer IN ('L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6')
        GROUP BY n.layer
        ORDER BY count DESC
    """)

    print("\n=== Write-Through by Layer ===\n")
    for layer, count in cur.fetchall():
        print(f"  [{layer}] {count:3d} edges")

    # Sample of actual writes_through operations
    cur.execute("""
        SELECT e.source_file, e.line_no, e.symbol, n.adg_name as target
        FROM edges e
        JOIN nodes n ON e.dst_id = n.id
        WHERE e.relation_type = 'writes_through'
        AND e.source_file LIKE 'agentic_core/%'
        LIMIT 10
    """)

    print("\n=== Sample Write-Through Operations ===\n")
    for file, line, symbol, target in cur.fetchall():
        print(f"  {file}:{line} -> {target}")
        if symbol:
            print(f"    Symbol: {symbol}")

    # Compare to other state mutation operations
    cur.execute("""
        SELECT relation_type, COUNT(*) as count
        FROM edges
        WHERE relation_type IN ('writes_through', 'modifies_state', 'updates_state')
        GROUP BY relation_type
        ORDER BY count DESC
    """)

    print("\n=== State Mutation Edge Types ===\n")
    for rel_type, count in cur.fetchall():
        print(f"  {rel_type:15s} {count:4d} edges")

    conn.close()


if __name__ == "__main__":
    main()
