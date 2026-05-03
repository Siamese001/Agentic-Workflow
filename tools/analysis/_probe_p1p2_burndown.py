"""One-shot: probe current P0/P1/P2 antipattern burndown counts."""
from __future__ import annotations

import glob
import os
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
snaps = sorted(
    glob.glob(str(REPO_ROOT / "artifacts/adg/adg_indexed_*.sqlite")),
    key=os.path.getmtime,
)
snap = snaps[-1]
print(f"snapshot: {Path(snap).name}")
conn = sqlite3.connect(snap)
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM violations")
print(f"total violations: {cur.fetchone()[0]}")
print()

cur.execute("PRAGMA table_info(violations)")
cols = [r[1] for r in cur.fetchall()]
print(f"violations cols: {cols}")
print()

# Group by first grouping-ish column
for gcol in ("severity", "category", "kind", "rule", "rule_id", "band", "type"):
    if gcol in cols:
        print(f"=== by {gcol} ===")
        for row in cur.execute(
            f"SELECT {gcol}, COUNT(*) FROM violations GROUP BY {gcol} ORDER BY 2 DESC LIMIT 30"
        ).fetchall():
            print(f"  {str(row[0]):40s} {row[1]:>6d}")
        print()

# Check p_band / severity from P-views
print("=== P0/P1/P2/P3 views (if present) ===")
for band in ("0", "1", "2", "3"):
    try:
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='view' AND name LIKE ? ORDER BY name",
            (f"v_p{band}_%",),
        )
        views = [r[0] for r in cur.fetchall()]
        total = 0
        for v in views:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {v}")
                total += cur.fetchone()[0]
            except sqlite3.Error:
                pass
        print(f"  P{band}: {len(views)} views, {total} rows")
    except sqlite3.Error as e:
        print(f"  P{band}: ERROR {e}")

print()
print("=== top 20 files by violation count ===")
if "source_file" in cols:
    for row in cur.execute(
        "SELECT source_file, COUNT(*) c FROM violations GROUP BY source_file ORDER BY c DESC LIMIT 20"
    ).fetchall():
        print(f"  {row[1]:>4d}  {row[0]}")
