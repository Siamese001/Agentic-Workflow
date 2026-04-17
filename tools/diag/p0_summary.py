"""Summarize all P0 structural_conformance violations grouped by file and hop."""

import sqlite3
import glob
import os
from collections import defaultdict

adg_dir = r"artifacts\adg"
snapshots = sorted(glob.glob(os.path.join(adg_dir, "adg_indexed_*.sqlite")))
db = snapshots[-1]

conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("""
    SELECT file_path, line_no, category, evidence
    FROM violations
    WHERE severity='P0' AND violation_class='structural_conformance'
    ORDER BY file_path, line_no
""")
rows = cur.fetchall()

by_file = defaultdict(list)
hop_counts = defaultdict(int)
for r in rows:
    by_file[r["file_path"]].append((r["line_no"], r["evidence"]))
    hop_counts[r["evidence"]] += 1

print(f"Total P0 structural_conformance violations: {len(rows)}")
print(f"Distinct files: {len(by_file)}\n")

print("=== By hop type ===")
for hop, cnt in sorted(hop_counts.items(), key=lambda x: -x[1]):
    print(f"  {hop}: {cnt}")

print("\n=== By file ===")
for f, lines in sorted(by_file.items()):
    hops = set(ev for _, ev in lines)
    print(f"  [{len(lines):3d}]  {f}")
    for hop in sorted(hops):
        print(f"         {hop}")

conn.close()
