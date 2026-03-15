#!/usr/bin/env python3
"""Find all time.time() / time.monotonic() lines in L1/L2/L3 core files."""

import os
import sqlite3

adg_dir = r"artifacts\adg"
sqls = sorted([f for f in os.listdir(adg_dir) if f.endswith(".sqlite")], reverse=True)
conn = sqlite3.connect(os.path.join(adg_dir, sqls[0]))
c = conn.cursor()

# Get all uses_wall_clock in L1/L2/L3 with line numbers
c.execute("""
    SELECT n.layer, n.resolved_path, e.line_no, e.symbol
    FROM edges e JOIN nodes n ON e.src_id=n.id
    WHERE e.relation_type='uses_wall_clock'
    AND n.layer IN ('L1','L2','L3')
    ORDER BY n.layer, n.resolved_path, e.line_no
""")
rows = c.fetchall()
print(f"Total L1/L2/L3 uses_wall_clock edges: {len(rows)}")
current_file = None
for r in rows:
    if r[1] != current_file:
        current_file = r[1]
        print(f"\n  [{r[0]}] {r[1]}")
    print(f"    line {r[2]:5}  {r[3]}")

conn.close()
