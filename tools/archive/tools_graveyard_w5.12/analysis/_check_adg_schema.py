import sqlite3

conn = sqlite3.connect("C:/Git/Agentic-Workflow/artifacts/adg/adg_indexed_04062026_1246.sqlite")
print("Source files with tools/adg:")
for row in conn.execute(
    'SELECT DISTINCT source_file FROM edges WHERE source_file LIKE "%tools/adg%" LIMIT 5'
):
    print(row[0])

print("\nEdge kinds with broad_exception_catch:")
for row in conn.execute('SELECT DISTINCT edge_kind FROM edges WHERE edge_kind LIKE "%exception%" LIMIT 10'):
    print(row[0])

conn.close()
