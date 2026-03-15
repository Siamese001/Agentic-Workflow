#!/usr/bin/env python3
"""Full L0 gap analysis - all remaining signals."""

import os
import sqlite3

adg_dir = r"artifacts\adg"
sqls = sorted([f for f in os.listdir(adg_dir) if f.endswith(".sqlite")], reverse=True)
conn = sqlite3.connect(os.path.join(adg_dir, sqls[0]))
c = conn.cursor()
print(f"DB: {sqls[0]}")

# 1. uses_wall_clock in L0/L1/L2/L3 (core layers only - these matter most)
print("\n=== uses_wall_clock in core layers (L0-L5) ===")
c.execute("""
    SELECT n.layer, n.resolved_path, e.line_no, e.symbol, COUNT(*) as cnt
    FROM edges e JOIN nodes n ON e.src_id=n.id
    WHERE e.relation_type='uses_wall_clock'
    AND n.layer IN ('L0','L1','L2','L3','L4','L5')
    GROUP BY n.layer, n.resolved_path
    ORDER BY n.layer, cnt DESC
""")
rows = c.fetchall()
print(f"Total: {len(rows)} files")
for r in rows:
    print(f"  [{r[0]:4}] cnt={r[4]:3}  {r[1]}")

# 2. invokes_getattr_dynamic in L0 specifically
print("\n=== invokes_getattr_dynamic in L0 only ===")
c.execute("""
    SELECT n.resolved_path, e.line_no, e.symbol
    FROM edges e JOIN nodes n ON e.src_id=n.id
    WHERE e.relation_type='invokes_getattr_dynamic'
    AND n.layer='L0'
    ORDER BY n.resolved_path, e.line_no
    LIMIT 40
""")
for r in c.fetchall():
    print(f"  line {r[1]:5}  sym={r[2]:40}  {r[0]}")

# 3. Check execute_ssot.py getattr specifically
print("\n=== execute_ssot.py getattr_dynamic details ===")
c.execute("""
    SELECT e.line_no, e.symbol FROM edges e JOIN nodes n ON e.src_id=n.id
    WHERE e.relation_type='invokes_getattr_dynamic'
    AND n.resolved_path='agentic_core/L0_routing/scripts/execute_ssot.py'
    ORDER BY e.line_no
""")
for r in c.fetchall():
    print(f"  line {r[0]:5}  {r[1]}")

# 4. What's uses_wall_clock in L0 still?
print("\n=== uses_wall_clock remaining in L0 ===")
c.execute("""
    SELECT e.line_no, e.symbol, n.resolved_path FROM edges e JOIN nodes n ON e.src_id=n.id
    WHERE e.relation_type='uses_wall_clock' AND n.layer='L0'
    ORDER BY n.resolved_path, e.line_no
""")
for r in c.fetchall():
    print(f"  line {r[0]:5}  sym={r[1]:40}  {r[2]}")

conn.close()
