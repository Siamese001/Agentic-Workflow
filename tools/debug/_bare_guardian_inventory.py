"""W6.1-P0 inventory: count BARE-guardian candidate sites per layer.

Queries the latest ADG snapshot's violations table and groups bare/guardian-
adjacent antipattern types by layer to produce the 1696-site breakdown
referenced in the prior plan's Non-Goals.
"""
from __future__ import annotations

import sqlite3
from collections import Counter
from pathlib import Path

snap = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"))[-1]
print(f"snapshot={snap.name}\n")

con = sqlite3.connect(str(snap))
cur = con.cursor()

# Distinct antipattern types in violations
cur.execute("PRAGMA table_info(violations)")
print("== violations schema ==")
for r in cur.fetchall():
    print(f"  {r}")
print()
cur.execute("SELECT category, COUNT(*) FROM violations GROUP BY category ORDER BY 2 DESC LIMIT 30")
print("== top 30 violation_type ==")
for row in cur.fetchall():
    print(f"  {row[1]:>5}  {row[0]}")
print()

# Filter to bare-except / broad-catch patterns
cur.execute(
    "SELECT evidence, COUNT(*) FROM violations WHERE "
    "LOWER(category) LIKE '%bare%' OR LOWER(category) LIKE '%broad%' "
    "OR LOWER(category) LIKE '%guardian%' OR LOWER(category) LIKE '%except%' "
    "OR LOWER(category) LIKE '%swallow%' OR LOWER(evidence) LIKE '%bare%' "
    "OR LOWER(evidence) LIKE '%broad%' OR LOWER(evidence) LIKE '%except exception%' "
    "GROUP BY evidence ORDER BY 2 DESC LIMIT 20"
)
print("== top 20 bare/broad/guardian evidence ==")
for row in cur.fetchall():
    print(f"  {row[1]:>5}  {row[0][:120]}")
print()

# Layer breakdown using file_path prefix
cur.execute(
    "SELECT CASE "
    "  WHEN file_path LIKE 'agentic_core/L0_%' THEN 'L0' "
    "  WHEN file_path LIKE 'agentic_core/L1_%' THEN 'L1' "
    "  WHEN file_path LIKE 'agentic_core/L2_%' THEN 'L2' "
    "  WHEN file_path LIKE 'agentic_core/L3_%' THEN 'L3' "
    "  WHEN file_path LIKE 'agentic_core/L4_%' THEN 'L4' "
    "  WHEN file_path LIKE 'agentic_core/L5_%' THEN 'L5' "
    "  WHEN file_path LIKE 'agentic_core/L6_%' THEN 'L6' "
    "  WHEN file_path LIKE 'apps_%' THEN 'L_APP' "
    "  WHEN file_path LIKE 'tools/%' THEN 'L_TOOLS' "
    "  WHEN file_path LIKE 'ops_scripts/%' THEN 'L_OPS' "
    "  ELSE 'other' END AS layer, COUNT(*) AS n "
    "FROM violations "
    "WHERE LOWER(category) LIKE '%bare%' OR LOWER(category) LIKE '%broad%' "
    "OR LOWER(category) LIKE '%except%' OR LOWER(evidence) LIKE '%except exception%' "
    "GROUP BY layer ORDER BY n DESC"
)
print("== bare/broad/except by layer ==")
for row in cur.fetchall():
    print(f"  {row[1]:>5}  {row[0]}")
