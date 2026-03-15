import sqlite3

conn = sqlite3.connect("artifacts/adg/adg_indexed_03142026_2228.sqlite")

print("records_execution_trace edges:")
cursor = conn.execute(
    'SELECT source_file, symbol FROM edges WHERE relation_type="records_execution_trace" AND source_file NOT LIKE "%test%" AND source_file NOT LIKE "%tests%" AND source_file NOT LIKE "%spec%" AND source_file NOT LIKE "%fixture%" AND source_file NOT LIKE "%mock%" LIMIT 5'
)
results = cursor.fetchall()
for r in results:
    print(" ", r)

print("\nAll relation types:")
cursor = conn.execute("SELECT DISTINCT relation_type FROM edges ORDER BY relation_type")
results = cursor.fetchall()
for r in results:
    print(" ", r[0])

conn.close()
