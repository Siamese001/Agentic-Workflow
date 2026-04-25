import sqlite3
from pathlib import Path

p = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda x: x.stat().st_mtime)[-1]
c = sqlite3.connect(p)
print(f"snap: {p.name}")
print("\nmv_capability_and_egress_gaps rows (gap_type != 'ok'):")
for r in c.execute("SELECT gap_type, file FROM mv_capability_and_egress_gaps WHERE gap_type != 'ok'"):
    print(f"  {r[0]}  {r[1]}")
