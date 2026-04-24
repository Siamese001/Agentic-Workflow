"""Enumerate all views in latest ADG snapshot to locate SC-1 analog."""
from __future__ import annotations

import sqlite3
from pathlib import Path

snap = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"))[-1]
con = sqlite3.connect(str(snap))
cur = con.cursor()

print(f"snapshot={snap.name}\n")

# All views
cur.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
views = [r[0] for r in cur.fetchall()]
print(f"== {len(views)} views ==")
for v in views:
    print(f"  {v}")

print()

# All tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cur.fetchall()]
print(f"== {len(tables)} tables ==")
for t in tables:
    print(f"  {t}")

# Check violations table if it exists
if "violations" in tables:
    print("\n== violations.category values ==")
    cur.execute("SELECT DISTINCT category FROM violations ORDER BY category")
    for r in cur.fetchall():
        print(f"  {r[0]}")
    print("\n== violations row count ==")
    cur.execute("SELECT COUNT(*) FROM violations")
    print(f"  total={cur.fetchone()[0]}")
    cur.execute("SELECT category, COUNT(*) FROM violations GROUP BY category ORDER BY 2 DESC")
    print("\n== violations by category ==")
    for r in cur.fetchall():
        print(f"  {r[0]}\t{r[1]}")
