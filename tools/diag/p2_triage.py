"""Triage MEDIUM antipattern P2 ratchet failure."""

import glob
import os
import sqlite3

import sys
import tempfile
from agentic_core.L0_routing.config.path_constants import ADG_ARTIFACTS_DIR

if len(sys.argv) > 1:
    db = sys.argv[1]
else:
    candidates = glob.glob(f"{ADG_ARTIFACTS_DIR}/adg_indexed_*.sqlite") + glob.glob(
        os.path.join(tempfile.gettempdir(), "adg_temp_*", "adg", "adg_indexed_*.sqlite")
    )
    candidates = [c for c in candidates if "smoketest" not in c]
    db = sorted(candidates, key=os.path.getmtime)[-1]
print(f"DB: {db}")
conn = sqlite3.connect(db)
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM violations WHERE severity='MEDIUM' AND category='antipattern'")
print(f"MEDIUM antipattern total: {cur.fetchone()[0]}")

cur.execute("PRAGMA table_info(violations)")
cols = [r[1] for r in cur.fetchall()]
print(f"\nviolations columns: {cols}")
kind_col = "rule_id" if "rule_id" in cols else ("kind" if "kind" in cols else cols[0])
file_col = "file_path" if "file_path" in cols else ("path" if "path" in cols else "file")

cur.execute(
    f"SELECT {kind_col}, COUNT(*) c FROM violations "
    "WHERE severity='MEDIUM' AND category='antipattern' "
    f"GROUP BY {kind_col} ORDER BY c DESC"
)
print(f"\nBy {kind_col}:")
for k, v in cur.fetchall():
    print(f"  {v:5d}  {k}")

cur.execute(
    f"SELECT {file_col}, COUNT(*) c FROM violations "
    "WHERE severity='MEDIUM' AND category='antipattern' "
    f"GROUP BY {file_col} ORDER BY c DESC LIMIT 25"
)
print("\nTop 25 files:")
for f, v in cur.fetchall():
    print(f"  {v:4d}  {f}")
