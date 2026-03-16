import sqlite3

db = r"c:/Git/Agentic-Workflow/artifacts/adg/adg_indexed_03162026_0908.sqlite"
with sqlite3.connect(db) as con:
    cur = con.cursor()
    tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    print("TABLES", tables)
    cols = cur.execute("PRAGMA table_info(edges)").fetchall()
    print("EDGES_COLS", cols)
    print("SAMPLE", cur.execute("SELECT * FROM edges LIMIT 3").fetchall())
