"""Probe MEDIUM violations in the latest ADG snapshot."""
import sqlite3
import json
from pathlib import Path

from datetime import datetime as _dt
def _valid(p):
    try:
        _dt.strptime(p.stem.replace("adg_indexed_", ""), "%m%d%Y_%H%M")
        return True
    except ValueError:
        return False
db = sorted([p for p in Path("artifacts/adg").glob("adg_indexed_*.sqlite") if _valid(p)])[-1]
print(f"Snapshot: {db}")
con = sqlite3.connect(db)

rows = con.execute(
    """
    SELECT v.file_path, v.line_no, v.category, v.evidence, v.disposition, v.severity, e.edge_kind
    FROM violations v LEFT JOIN edges e ON v.edge_id = e.id
    WHERE v.severity = 'MEDIUM'
    ORDER BY v.file_path, v.line_no
    """
).fetchall()

for fp, ln, cat, ev_raw, disp, sev, ek in rows:
    print(f"  {fp}:{ln}  edge_kind={ek}  disp={disp}")

print()
print(f"Total MEDIUM: {len(rows)}")

# Also show by category
from collections import Counter
by_cat = Counter(r[2] for r in rows)
print("By category:", dict(by_cat))
by_disp = Counter(r[4] for r in rows)
print("By disposition:", dict(by_disp))
con.close()
