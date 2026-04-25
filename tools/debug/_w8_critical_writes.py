"""Show all critical write_sovereignty entries with symbols."""

import sqlite3
from pathlib import Path

snap = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime)[-1]
c = sqlite3.connect(snap)
print(f"snapshot: {snap.name}\n")
print("=== critical writes ===")
for row in c.execute(
    "SELECT writer_file, write_symbol, COUNT(*) FROM mv_write_sovereignty_paths "
    "WHERE severity='critical' GROUP BY writer_file, write_symbol ORDER BY writer_file"
):
    print(f"  {row[2]}x  {row[0]}  ::  {row[1]}")
