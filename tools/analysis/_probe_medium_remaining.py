"""List remaining MEDIUM antipattern sites after W2."""
from __future__ import annotations

import glob
import os
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
snap = sorted(
    glob.glob(str(REPO_ROOT / "artifacts/adg/adg_indexed_*.sqlite")),
    key=os.path.getmtime,
)[-1]
print(f"snapshot: {Path(snap).name}\n")
conn = sqlite3.connect(snap)
cur = conn.cursor()

cur.execute(
    """
    SELECT file_path, line_no, category, violation_class, evidence
    FROM violations
    WHERE severity = 'MEDIUM'
    ORDER BY file_path, line_no
    """
)
rows = cur.fetchall()
print(f"MEDIUM total: {len(rows)}\n")
for r in rows:
    print(f"  {r[0]}:{r[1]}  cat={r[2]} class={r[3]}  ev={r[4]}")
