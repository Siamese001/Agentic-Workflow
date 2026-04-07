"""Query applies_guardrail coverage from ADG SQLite database."""
import sqlite3
from pathlib import Path


def query_guardrail_coverage():
    adg_dir = Path(__file__).resolve().parents[2] / 'artifacts' / 'adg'
    sqlite_files = list(adg_dir.glob('adg_indexed_*.sqlite'))
    if not sqlite_files:
        print("No ADG SQLite files found")
        return

    latest_sqlite = max(sqlite_files, key=lambda p: p.stat().st_mtime)
    print(f"Querying: {latest_sqlite.name}\n")

    conn = sqlite3.connect(latest_sqlite)
    cur = conn.cursor()

    # Get total applies_guardrail edges
    cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type = 'applies_guardrail'")
    total_guardrail = cur.fetchone()[0]
    print(f"Total applies_guardrail edges: {total_guardrail}\n")

    # Get files with guardrail coverage
    cur.execute("""
        SELECT source_file, COUNT(*) as cnt
        FROM edges
        WHERE relation_type = 'applies_guardrail'
        GROUP BY source_file
        ORDER BY cnt DESC
    """)

    by_file = cur.fetchall()
    print(f"Files with guardrail coverage: {len(by_file)}\n")

    print("=== Top 20 Files by Guardrail Coverage ===\n")
    for file_path, count in by_file[:20]:
        print(f"{file_path}: {count} sites")

    # Get layer distribution
    print("\n=== Guardrail Coverage by Layer ===\n")
    cur.execute("""
        SELECT
            CASE
                WHEN source_file LIKE '%/L0_%' THEN 'L0'
                WHEN source_file LIKE '%/L1_%' THEN 'L1'
                WHEN source_file LIKE '%/L2_%' THEN 'L2'
                WHEN source_file LIKE '%/L3_%' THEN 'L3'
                WHEN source_file LIKE '%/L4_%' THEN 'L4'
                WHEN source_file LIKE '%/L5_%' THEN 'L5'
                WHEN source_file LIKE '%/L6_%' THEN 'L6'
                WHEN source_file LIKE 'apps_%' THEN 'L_APP'
                WHEN source_file LIKE 'tools/%' THEN 'L_TOOLS'
                WHEN source_file LIKE 'ops_scripts/%' THEN 'L_OPS'
                ELSE 'OTHER'
            END as layer,
            COUNT(*) as cnt
        FROM edges
        WHERE relation_type = 'applies_guardrail'
        GROUP BY layer
        ORDER BY cnt DESC
    """)

    for layer, count in cur.fetchall():
        print(f"{layer}: {count} sites")

    # Get target operations
    print("\n=== Guardrail Target Operations (Top 20) ===\n")
    cur.execute("""
        SELECT symbol, COUNT(*) as cnt
        FROM edges
        WHERE relation_type = 'applies_guardrail'
        GROUP BY symbol
        ORDER BY cnt DESC
        LIMIT 20
    """)

    for symbol, count in cur.fetchall():
        print(f"{symbol}: {count}")

    # Compare with total dispatch/execution sites
    print("\n=== Coverage Analysis ===\n")

    cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type = 'calls'")
    total_calls = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type = 'calls'")
    files_with_calls = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type = 'applies_guardrail'")
    files_with_guardrails = cur.fetchone()[0]

    print(f"Total function calls: {total_calls}")
    print(f"Files with calls: {files_with_calls}")
    print(f"Files with guardrails: {files_with_guardrails}")
    print(f"Guardrail coverage: {files_with_guardrails}/{files_with_calls} files ({100*files_with_guardrails/files_with_calls:.1f}%)")

    conn.close()

if __name__ == '__main__':
    query_guardrail_coverage()
