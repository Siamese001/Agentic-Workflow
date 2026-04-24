"""Verify guardian exemption logic against existing ADG snapshot."""

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sqlite_path = Path("artifacts/adg/adg_indexed_04062026_2106.sqlite")

conn = sqlite3.connect(str(sqlite_path))
cursor = conn.cursor()

cursor.execute("SELECT source_file, line_no FROM edges WHERE relation_type='violates'")
violation_rows = cursor.fetchall()

print(f"Total violations: {len(violation_rows)}")

unapproved = []
for source_file, line_no in violation_rows:
    try:
        src_path = ROOT / source_file
        if src_path.exists() and line_no and line_no > 0:
            lines = src_path.read_text(encoding="utf-8", errors="ignore").splitlines()
            check_lines = lines[max(0, line_no - 2) : line_no]
            exempted = any("guardian: allow-layer-violation" in ln for ln in check_lines)
            if not exempted:
                unapproved.append((source_file, line_no))
            else:
                print(f"EXEMPTED: {source_file}:{line_no}")
        else:
            print(f"FILE NOT FOUND: {source_file}:{line_no}")
            unapproved.append((source_file, line_no))
    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        print(f"EXCEPTION for {source_file}:{line_no}: {e}")
        unapproved.append((source_file, line_no))

print(f"\nUnapproved violations: {len(unapproved)}")
for sf, ln in unapproved:
    print(f"  {sf}:{ln}")

conn.close()
