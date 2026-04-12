import sqlite3

conn = sqlite3.connect("artifacts/adg/adg_indexed_04062026_0952.sqlite")
cursor = conn.cursor()

cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print("Tables:", [t[0] for t in tables])

cursor.execute("PRAGMA table_info(nodes)")
print("\nNodes schema:", cursor.fetchall())

cursor.execute("PRAGMA table_info(edges)")
print("\nEdges schema:", cursor.fetchall())

conn.close()
