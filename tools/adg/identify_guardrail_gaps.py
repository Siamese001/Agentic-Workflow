"""Identify operations that should have guardrails but don't."""
import sqlite3
from pathlib import Path
from collections import defaultdict

def identify_guardrail_gaps():
    adg_dir = Path(__file__).resolve().parents[2] / 'artifacts' / 'adg'
    sqlite_files = list(adg_dir.glob('adg_indexed_*.sqlite'))
    if not sqlite_files:
        print("No ADG SQLite files found")
        return

    latest_sqlite = max(sqlite_files, key=lambda p: p.stat().st_mtime)
    print(f"Querying: {latest_sqlite.name}\n")

    conn = sqlite3.connect(latest_sqlite)
    cur = conn.cursor()

    # High-risk edge types that should have guardrails
    high_risk_edges = [
        'accesses_credential',
        'external_http_call',
        'reads_secret',
        'invokes_dynamic',
        'invokes_eval',
        'invokes_importlib',
    ]

    print("=== High-Risk Operations Without Guardrails ===\n")

    for edge_type in high_risk_edges:
        # Get files with this edge type
        cur.execute(f"""
            SELECT DISTINCT source_file
            FROM edges
            WHERE relation_type = '{edge_type}'
        """)
        files_with_risk = set(row[0] for row in cur.fetchall())

        # Get files with guardrails
        cur.execute("""
            SELECT DISTINCT source_file
            FROM edges
            WHERE relation_type = 'applies_guardrail'
        """)
        files_with_guardrails = set(row[0] for row in cur.fetchall())

        # Find gap
        gap_files = files_with_risk - files_with_guardrails

        if gap_files:
            print(f"\n{edge_type}: {len(gap_files)} files without guardrails")
            for f in sorted(gap_files)[:10]:  # Show first 10
                # Get count of this edge type in file
                cur.execute(f"""
                    SELECT COUNT(*)
                    FROM edges
                    WHERE relation_type = '{edge_type}' AND source_file = ?
                """, (f,))
                count = cur.fetchone()[0]
                print(f"  {f} ({count} sites)")
            if len(gap_files) > 10:
                print(f"  ... and {len(gap_files) - 10} more files")

    # Check AgentDispatchRegistry usage without guardrails
    print("\n\n=== AgentDispatchRegistry.dispatch() Without Guardrails ===\n")
    cur.execute("""
        SELECT source_file, COUNT(*) as cnt
        FROM edges
        WHERE symbol LIKE '%AgentDispatchRegistry%dispatch%'
        AND source_file NOT IN (
            SELECT DISTINCT source_file
            FROM edges
            WHERE relation_type = 'applies_guardrail'
        )
        GROUP BY source_file
        ORDER BY cnt DESC
        LIMIT 20
    """)

    dispatch_gaps = cur.fetchall()
    if dispatch_gaps:
        print(f"Found {len(dispatch_gaps)} files using dispatch without guardrails:\n")
        for file_path, count in dispatch_gaps:
            print(f"{file_path}: {count} dispatch calls")
    else:
        print("All dispatch calls have guardrail coverage ✓")

    # Check LLM client usage without guardrails
    print("\n\n=== LLM Client Usage Without Guardrails ===\n")
    cur.execute("""
        SELECT source_file, symbol, COUNT(*) as cnt
        FROM edges
        WHERE (
            symbol LIKE '%openai%' OR
            symbol LIKE '%anthropic%' OR
            symbol LIKE '%gemini%' OR
            symbol LIKE '%LLM%' OR
            symbol LIKE '%llm%'
        )
        AND relation_type = 'calls'
        AND source_file NOT IN (
            SELECT DISTINCT source_file
            FROM edges
            WHERE relation_type = 'applies_guardrail'
        )
        AND source_file NOT LIKE 'tests/%'
        GROUP BY source_file, symbol
        ORDER BY cnt DESC
        LIMIT 20
    """)

    llm_gaps = cur.fetchall()
    if llm_gaps:
        print(f"Found {len(llm_gaps)} LLM usage patterns without guardrails:\n")
        for file_path, symbol, count in llm_gaps:
            print(f"{file_path}: {symbol} ({count} calls)")

    # Summary
    print("\n\n=== Wave 4 Target Summary ===\n")

    total_high_risk = 0
    for edge_type in high_risk_edges:
        cur.execute(f"SELECT COUNT(*) FROM edges WHERE relation_type = '{edge_type}'")
        count = cur.fetchone()[0]
        total_high_risk += count
        print(f"{edge_type}: {count} edges")

    cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type = 'applies_guardrail'")
    current_guardrails = cur.fetchone()[0]

    print(f"\nTotal high-risk edges: {total_high_risk}")
    print(f"Current guardrail coverage: {current_guardrails} edges")
    print(f"Coverage ratio: {100*current_guardrails/max(total_high_risk,1):.1f}%")

    conn.close()

if __name__ == '__main__':
    identify_guardrail_gaps()
