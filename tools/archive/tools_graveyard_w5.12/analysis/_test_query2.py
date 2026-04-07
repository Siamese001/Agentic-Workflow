import sqlite3
from pathlib import Path

sqlite_path = Path("C:/Git/Agentic-Workflow/artifacts/adg/adg_indexed_04062026_1246.sqlite")

pipeline_paths = ("tools/adg/%", "tools/generate/%", "agentic_core/adg/%")
swallow_types = ("silent_exception_swallow", "broad_exception_catch", "log_and_swallow", "return_none_swallow")

query = """
    SELECT COUNT(*)
    FROM edges e
    WHERE e.edge_kind IN (?, ?, ?, ?)
    AND (
        e.source_file LIKE ?
        OR e.source_file LIKE ?
        OR e.source_file LIKE ?
    )
"""

with sqlite3.connect(str(sqlite_path)) as conn:
    cursor = conn.cursor()
    cursor.execute(query, (*swallow_types, *pipeline_paths))
    count = cursor.fetchone()[0]
    print(f"Count with %: {count}")
