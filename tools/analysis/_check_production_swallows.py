import sqlite3
from pathlib import Path

sqlite_path = Path("C:/Git/Agentic-Workflow/artifacts/adg/adg_indexed_04062026_1246.sqlite")

# Production paths (excluding pipeline paths and test scaffolding)
production_paths = ("apps_/%", "agentic_core/L0/%", "agentic_core/L1/%", "agentic_core/L2/%", "agentic_core/L3/%", "system_learning/%")
swallow_types = ("silent_exception_swallow", "broad_exception_catch", "log_and_swallow", "return_none_swallow")

query = """
    SELECT COUNT(*)
    FROM edges e
    WHERE e.edge_kind IN (?, ?, ?, ?)
    AND (
        e.source_file LIKE ?
        OR e.source_file LIKE ?
        OR e.source_file LIKE ?
        OR e.source_file LIKE ?
        OR e.source_file LIKE ?
        OR e.source_file LIKE ?
    )
"""

with sqlite3.connect(str(sqlite_path)) as conn:
    cursor = conn.cursor()
    cursor.execute(query, (*swallow_types, *production_paths))
    count = cursor.fetchone()[0]
    print(f"Exception swallows in production paths: {count}")

    # Show breakdown by path
    for path in production_paths:
        cursor.execute("SELECT COUNT(*) FROM edges WHERE edge_kind IN (?, ?, ?, ?) AND source_file LIKE ?", (*swallow_types, path))
        path_count = cursor.fetchone()[0]
        if path_count > 0:
            print(f"  {path}: {path_count}")
