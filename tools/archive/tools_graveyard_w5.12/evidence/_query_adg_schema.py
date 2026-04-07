import sqlite3

DB = r"c:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03132026_0558.sqlite"
conn = sqlite3.connect(DB)
c = conn.cursor()

# Schema
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", c.fetchall())

c.execute("PRAGMA table_info(edges)")
print("Edges schema:", c.fetchall())

c.execute("PRAGMA table_info(nodes)")
print("Nodes schema:", c.fetchall())

c.execute("PRAGMA table_info(meta)")
print("Meta schema:", c.fetchall())

c.execute("SELECT * FROM meta")
print("Meta rows:", c.fetchall())

# Sample edges
c.execute("SELECT * FROM edges LIMIT 5")
print("Sample edges:", c.fetchall())

conn.close()
