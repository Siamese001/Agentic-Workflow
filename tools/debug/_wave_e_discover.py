"""Wave E discovery: find duplicate adapter patterns via ADG P-views."""

from __future__ import annotations

import sqlite3

c = sqlite3.connect("artifacts/adg/adg_indexed_04232026_1442.sqlite")

# Discover relevant views
print("=== Tables/views with 'dup' or 'adapter' ===")
q = (
    "SELECT name, type FROM sqlite_master "
    "WHERE (name LIKE '%dup%' OR name LIKE '%adapter%') "
    "AND type IN ('view','table') ORDER BY name"
)
for name, kind in c.execute(q):
    print(f"  [{kind:5}] {name}")

# Try v_p2_duplicated_adapters if it exists
print("\n=== v_p2_duplicated_adapters (top 20) ===")
try:
    rows = list(c.execute("SELECT * FROM v_p2_duplicated_adapters LIMIT 20"))
    if rows:
        cols = [d[0] for d in c.execute("SELECT * FROM v_p2_duplicated_adapters LIMIT 1").description]
        print("cols:", cols)
        for r in rows:
            print(f"  {r}")
    else:
        print("(empty)")
except sqlite3.OperationalError as e:
    print(f"(no such view: {e})")

# Alternate P-views
for vn in ("v_p2_duplicated_services", "v_p2_duplicate", "mv_duplicates"):
    try:
        n = c.execute(f"SELECT COUNT(*) FROM {vn}").fetchone()[0]
        print(f"\n{vn}: {n} rows")
    except sqlite3.OperationalError:
        pass
