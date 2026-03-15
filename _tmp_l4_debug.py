"""Debug P0/L4 gap: how does ADG detect observes_runtime_state and snapshots_state edges?"""

import glob
import os
import sqlite3

os.chdir(r"C:\Git\Agentic-Workflow")

dbs = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))
db = dbs[-1]
print(f"DB: {db}")
conn = sqlite3.connect(db)
c = conn.cursor()

print("\n=== ALL snapshots_state edges (incl test) ===")
c.execute(
    "SELECT source_file, symbol, line_no FROM edges"
    " WHERE relation_type='snapshots_state'"
    " ORDER BY source_file"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== ALL observes_runtime_state edges (incl test) ===")
c.execute(
    "SELECT source_file, symbol, line_no FROM edges"
    " WHERE relation_type='observes_runtime_state'"
    " ORDER BY source_file"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== ALL writes_through edges (incl test) ===")
c.execute(
    "SELECT source_file, symbol, line_no FROM edges"
    " WHERE relation_type='writes_through'"
    " ORDER BY source_file LIMIT 20"
)
for r in c.fetchall():
    print(" ", r)

# Look at the ADG schema to understand how these edge types are detected
print("\n=== Schema: how are observes_runtime_state/snapshots_state detected? ===")
c.execute(
    "SELECT DISTINCT relation_type, symbol FROM edges"
    " WHERE relation_type IN ('observes_runtime_state', 'snapshots_state', 'writes_through')"
    " LIMIT 30"
)
for r in c.fetchall():
    print(" ", r)

conn.close()
