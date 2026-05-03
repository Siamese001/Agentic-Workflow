"""List the specific MEDIUM/HIGH/CRITICAL/P2 items from the current snapshot."""
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

for sev in ("CRITICAL", "HIGH", "MEDIUM", "P2"):
    cur.execute(
        """
        SELECT file_path, line_no, category, violation_class, evidence, disposition
        FROM violations
        WHERE severity = ?
        ORDER BY file_path, line_no
        """,
        (sev,),
    )
    rows = cur.fetchall()
    print(f"=== {sev} ({len(rows)}) ===")
    for r in rows:
        path, line, cat, vcls, ev, disp = r
        ev_short = (ev[:70].replace("\n", " ") if ev else "")
        print(f"  {path}:{line}  cat={cat} class={vcls} disp={disp}  ev={ev_short}")
    print()

# Also show v_p2 views
for vname in ("v_p2_duplicated_adapters", "v_p2_mixed_usage", "v_p2_isolated_experimental"):
    try:
        cur.execute(f"SELECT COUNT(*) FROM {vname}")
        n = cur.fetchone()[0]
        if n:
            print(f"--- {vname} ({n}) ---")
            cur.execute(f"PRAGMA table_info({vname})")
            cols = [c[1] for c in cur.fetchall()]
            cur.execute(f"SELECT * FROM {vname}")
            for r in cur.fetchall():
                print(f"  {dict(zip(cols, r))}")
    except sqlite3.Error as e:
        print(f"  ERROR {vname}: {e}")
