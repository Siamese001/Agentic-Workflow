"""Find the net-new P1 (HIGH) antipattern delta."""

import glob
import os
import sqlite3
import tempfile

from collections import Counter
from agentic_core.L0_routing.config.path_constants import ADG_ARTIFACTS_DIR

f"{ADG_ARTIFACTS_DIR}/adg_indexed_*.sqlite"
dbs = sorted(glob.glob(f"{ADG_ARTIFACTS_DIR}/adg_indexed_*.sqlite"), key=os.path.getmtime)
NEW = dbs[-1]
OLD = dbs[-2]
print(f"NEW: {NEW}")
print(f"OLD: {OLD}")


def high_rows(db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(
        "SELECT file_path, line_no, evidence FROM violations WHERE severity='HIGH' AND category='antipattern'"
    )
    return set(cur.fetchall())


new_rows = high_rows(NEW)
old_rows = high_rows(OLD)
print(f"NEW total: {len(new_rows)}")
print(f"OLD total: {len(old_rows)}")

added = new_rows - old_rows
removed = old_rows - new_rows
print(f"Added: {len(added)}  Removed: {len(removed)}  Net: {len(added) - len(removed)}")

print("\n=== ADDED ===")
for f, ln, e in sorted(added):
    print(f"  {f}:{ln}  {e[:100]}")

print("\n=== REMOVED ===")
for f, ln, e in sorted(removed):
    print(f"  {f}:{ln}  {e[:100]}")
