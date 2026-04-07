import sqlite3
from pathlib import Path

sqlite_path = Path("C:/Git/Agentic-Workflow/artifacts/adg/adg_indexed_04062026_1447.sqlite")

with sqlite3.connect(str(sqlite_path)) as conn:
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM edges WHERE relation_type='violates'")
    violates_count = cursor.fetchone()[0]
    print(f"Violates edges (P1 critical): {violates_count}")

    if violates_count > 0:
        print("\nAll violates edges:")
        for row in cursor.execute("""
            SELECT source_file, line_no, relation_type, edge_kind
            FROM edges
            WHERE relation_type='violates'
        """):
            print(row)
