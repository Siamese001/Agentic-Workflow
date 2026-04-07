"""Probe ADG SQLite schema and sample data for behavioral signal analysis."""

import sqlite3
from pathlib import Path

DB = Path(r"c:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03132026_0745.sqlite")
con = sqlite3.connect(DB)
cur = con.cursor()

# Tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [t[0] for t in cur.fetchall()]
print("TABLES:", tables)

for t in tables:
    cur.execute(f"PRAGMA table_info({t})")
    cols = [c[1] for c in cur.fetchall()]
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    count = cur.fetchone()[0]
    print(f"\n{t} ({count} rows): {cols}")

# Get actual node columns first
cur.execute("PRAGMA table_info(nodes)")
node_cols = [c[1] for c in cur.fetchall()]
print("\nNODE COLUMNS:", node_cols)

# Sample a node to see what fields are populated
print("\n--- SAMPLE NODE (FileClassificationAgent) ---")
# find the right path-like column
path_col = next(
    (c for c in node_cols if "path" in c.lower() or "file" in c.lower() or "name" in c.lower()), node_cols[0],
)
cur.execute(f"SELECT * FROM nodes WHERE {path_col} LIKE '%FileClassificationAgent%' LIMIT 1")
row = cur.fetchone()
if row:
    print(dict(zip(node_cols, row)))

# Sample edges from/to that node
print("\n--- SAMPLE EDGES ---")
cur.execute("""
    SELECT relation_type, COUNT(*) as cnt
    FROM edges
    GROUP BY relation_type
    ORDER BY cnt DESC
""")
for r in cur.fetchall():
    print(r)

# Check meta table if exists
if "meta" in tables:
    cur.execute("SELECT * FROM meta LIMIT 5")
    print("\n--- META ---", cur.fetchall())

con.close()
