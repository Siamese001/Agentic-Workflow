#!/usr/bin/env python3
"""Query ADG violations with histogram and P0-P4 split."""

import sqlite3
from pathlib import Path

adg_dir = Path("artifacts/adg")
db_files = sorted(adg_dir.glob("adg_indexed_*.sqlite"))
db_path = db_files[-1]

print(f"Using: {db_path.name}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print(f"\nTables: {tables}")

# Check if violations table exists
violations_table = None
for t in tables:
    if "violation" in t.lower():
        violations_table = t
        break

if not violations_table:
    print("No violations table found")
    conn.close()
    exit(1)

print(f"\nUsing table: {violations_table}")

# Get schema
cursor.execute(f"PRAGMA table_info({violations_table})")
columns = [c[1] for c in cursor.fetchall()]
print(f"Columns: {columns}")

# Get total
cursor.execute(f"SELECT COUNT(*) FROM {violations_table}")
total = cursor.fetchone()[0]
print(f"\n{'=' * 50}")
print(f"TOTAL VIOLATIONS: {total}")
print(f"{'=' * 50}")

# Get severity breakdown
if "severity" in columns:
    cursor.execute(
        f"SELECT severity, COUNT(*) FROM {violations_table} GROUP BY severity ORDER BY COUNT(*) DESC"
    )
    severity_data = cursor.fetchall()
    print("\n=== SEVERITY HISTOGRAM ===")
    for sev, cnt in severity_data:
        pct = (cnt / total) * 100
        bar = "█" * int(pct / 2)
        print(f"  {sev:12s}: {cnt:5d} ({pct:5.1f}%) {bar}")

# P0-P4 mapping
print("\n=== P0-P4 SEVERITY SPLIT ===")
p_map = {"P0": 0, "P1": 0, "P2": 0, "P3": 0, "P4": 0}

if "severity" in columns:
    cursor.execute(f"SELECT severity, COUNT(*) FROM {violations_table} GROUP BY severity")
    for sev, cnt in cursor.fetchall():
        sev_upper = str(sev).upper()
        if sev_upper in ["CRITICAL", "P0", "CRIT"]:
            p_map["P0"] += cnt
        elif sev_upper in ["HIGH", "P1", "HI", "MAJOR"]:
            p_map["P1"] += cnt
        elif sev_upper in ["MEDIUM", "P2", "MED", "MODERATE"]:
            p_map["P2"] += cnt
        elif sev_upper in ["LOW", "P3", "MINOR"]:
            p_map["P3"] += cnt
        elif sev_upper in ["INFO", "P4", "WARNING", "TRIVIAL"]:
            p_map["P4"] += cnt
        else:
            # Map unknown to P2 (medium) as default
            p_map["P2"] += cnt

for p, cnt in p_map.items():
    pct = (cnt / total) * 100 if total > 0 else 0
    bar = "█" * int(pct / 2)
    print(f"  {p}: {cnt:5d} ({pct:5.1f}%) {bar}")

# Violation type histogram
if "violation_type" in columns:
    cursor.execute(
        f"SELECT violation_type, COUNT(*) FROM {violations_table} GROUP BY violation_type ORDER BY COUNT(*) DESC"
    )
    type_data = cursor.fetchall()
    print("\n=== VIOLATION TYPE HISTOGRAM ===")
    for vtype, cnt in type_data[:15]:  # Top 15
        pct = (cnt / total) * 100
        bar = "█" * int(pct / 2)
        vtype_short = vtype[:30]
        print(f"  {vtype_short:30s}: {cnt:5d} ({pct:5.1f}%) {bar}")

# Category breakdown if available
if "category" in columns:
    cursor.execute(
        f"SELECT category, COUNT(*) FROM {violations_table} GROUP BY category ORDER BY COUNT(*) DESC"
    )
    cat_data = cursor.fetchall()
    print("\n=== CATEGORY HISTOGRAM ===")
    for cat, cnt in cat_data:
        pct = (cnt / total) * 100
        bar = "█" * int(pct / 2)
        print(f"  {cat:20s}: {cnt:5d} ({pct:5.1f}%) {bar}")

# Top files
if "file_path" in columns:
    cursor.execute(
        f"SELECT file_path, COUNT(*) FROM {violations_table} GROUP BY file_path ORDER BY COUNT(*) DESC LIMIT 10"
    )
    file_data = cursor.fetchall()
    print("\n=== TOP 10 FILES BY VIOLATION COUNT ===")
    for fpath, cnt in file_data:
        pct = (cnt / total) * 100
        fpath_short = fpath[-40:] if len(fpath) > 40 else fpath
        print(f"  {cnt:3d} ({pct:4.1f}%) ...{fpath_short}")

conn.close()
print("\n" + "=" * 50)
print("Query complete")
