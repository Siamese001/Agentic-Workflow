import sqlite3

conn = sqlite3.connect('C:/Git/Agentic-Workflow/artifacts/adg/adg_indexed_04062026_1246.sqlite')

pipeline_paths = ("tools/adg/", "tools/generate/", "agentic_core/adg/")
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

cursor = conn.cursor()
cursor.execute(query, (*swallow_types, *pipeline_paths))
count = cursor.fetchone()[0]

print(f"Exception swallows in pipeline paths: {count}")

# Show some examples
if count > 0:
    print("\nExamples:")
    for row in conn.execute("""
        SELECT source_file, edge_kind, line_no
        FROM edges e
        WHERE e.edge_kind IN (?, ?, ?, ?)
        AND (
            e.source_file LIKE ?
            OR e.source_file LIKE ?
            OR e.source_file LIKE ?
        )
        LIMIT 10
    """, (*swallow_types, *pipeline_paths)):
        print(row)

conn.close()
