"""Query P0 layer violations from the latest ADG SQLite snapshot."""

import sqlite3
import glob
import os

adg_dir = r"artifacts\adg"
snapshots = sorted(glob.glob(os.path.join(adg_dir, "adg_indexed_*.sqlite")))
db = snapshots[-1]
print(f"DB: {db}")

conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# List all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cur.fetchall()]
print("Tables:", tables)

# Find violation/layer tables
for t in tables:
    if any(k in t.lower() for k in ["viol", "layer", "p0", "boundary"]):
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        count = cur.fetchone()[0]
        print(f"  {t}: {count} rows")
        cur.execute(f"SELECT * FROM {t} LIMIT 3")
        cols = [d[0] for d in cur.description]
        print(f"    cols: {cols}")

# Try proj_violations for P0
if "proj_violations" in tables:
    cur.execute("SELECT DISTINCT violation_class, priority FROM proj_violations ORDER BY priority LIMIT 20")
    print("\nproj_violations classes/priorities:")
    for r in cur.fetchall():
        print(dict(r))

    cur.execute("SELECT * FROM proj_violations WHERE priority='P0' OR priority=0 LIMIT 20")
    rows = cur.fetchall()
    print(f"\nP0 rows in proj_violations: {len(rows)}")
    for r in rows:
        print(dict(r))

conn.close()
