"""Join MEDIUM violations to their edges to see edge_kind."""
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
    SELECT v.file_path, v.line_no, v.evidence, e.edge_kind, e.relation_type
    FROM violations v
    LEFT JOIN edges e ON v.edge_id = e.id
    WHERE v.severity = 'MEDIUM' AND v.category = 'antipattern'
    ORDER BY v.file_path, v.line_no
    """
)
print("=== MEDIUM antipattern with edge join ===")
for r in cur.fetchall():
    fp, ln, ev, ek, rt = r
    print(f"  {fp}:{ln}  edge_kind={ek}  rel={rt}  ev={ev}")
