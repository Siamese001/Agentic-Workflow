#!/usr/bin/env python3
"""Run SC-1 and SC-5 checks to populate violations."""

import sqlite3
import sys
from pathlib import Path

# Add tools to path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from tools.generate.validation.gates import _check_structural_conformance

# Find latest SQLite
adg_dir = Path("artifacts/adg")
sqlite_files = sorted(adg_dir.glob("adg_indexed_*.sqlite"))
sqlite_path = sqlite_files[-1]
print(f"Using: {sqlite_path.name}")

# Run SC checks
print("\n=== Running SC-1 and SC-5 checks ===")
results = _check_structural_conformance(sqlite_path)

print(f"Checks run: {len(results)}")
for check_id, result in results.items():
    print(f"  {check_id}: {result}")

# Check violations table
conn = sqlite3.connect(str(sqlite_path))
cur = conn.cursor()

print("\n=== Violations after SC checks ===")
cur.execute("SELECT category, COUNT(*) FROM violations WHERE category IN ('SC-1', 'SC-5') GROUP BY category")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

# Sample SC violations
print("\n=== Sample SC-1 violations ===")
cur.execute("""
    SELECT file_path, line_no, category 
    FROM violations 
    WHERE category = 'SC-1' 
    LIMIT 5
""")
for row in cur.fetchall():
    path = row[0][:40] if row[0] else "N/A"
    print(f"  {path}:{row[1]} [{row[2]}]")

print("\n=== Sample SC-5 violations ===")
cur.execute("""
    SELECT file_path, line_no, category 
    FROM violations 
    WHERE category = 'SC-5' 
    LIMIT 5
""")
rows = cur.fetchall()
if rows:
    for row in rows:
        path = row[0][:40] if row[0] else "N/A"
        print(f"  {path}:{row[1]} [{row[2]}]")
else:
    print("  (none found - spine may be complete or detection needs tuning)")

conn.close()
print("\n=== SC checks complete ===")
