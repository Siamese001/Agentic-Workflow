import sqlite3
from pathlib import Path

sqlite_path = Path("C:/Git/Agentic-Workflow/artifacts/adg/adg_indexed_04062026_1446.sqlite")

# Check for P1 defects (violates edges)
with sqlite3.connect(str(sqlite_path)) as conn:
    cursor = conn.cursor()
    
    # Check violates edges
    cursor.execute("SELECT COUNT(*) FROM edges WHERE relation_type='violates'")
    violates_count = cursor.fetchone()[0]
    print(f"Violates edges (P1 critical): {violates_count}")
    
    if violates_count > 0:
        print("\nSample violates edges:")
        for row in cursor.execute("""
            SELECT source_file, line_no, relation_type, edge_kind
            FROM edges
            WHERE relation_type='violates'
            LIMIT 5
        """):
            print(row)
    
    # Check in_cycle edges
    cursor.execute("SELECT COUNT(*) FROM edges WHERE relation_type='in_cycle'")
    in_cycle_count = cursor.fetchone()[0]
    print(f"\nIn-cycle edges (P1 Tier 1A): {in_cycle_count}")
    
    # Check dynamic_exec edges
    cursor.execute("SELECT COUNT(*) FROM edges WHERE relation_type='dynamic_exec'")
    dynamic_exec_count = cursor.fetchone()[0]
    print(f"Dynamic exec edges (P1 Tier 1B): {dynamic_exec_count}")
