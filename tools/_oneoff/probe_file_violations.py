"""Probe all violations in a single file from latest ADG snapshot."""
import sqlite3
import sys
from pathlib import Path
from datetime import datetime


def _valid(p):
    try:
        datetime.strptime(p.stem.replace("adg_indexed_", ""), "%m%d%Y_%H%M")
        return True
    except ValueError:
        return False


target = sys.argv[1] if len(sys.argv) > 1 else "agentic_core/L5_safety/reasoning/graph_aware_safety_monitor.py"
valid = [p for p in Path("artifacts/adg").glob("adg_indexed_*.sqlite") if _valid(p)]
db = sorted(valid)[-1]
con = sqlite3.connect(db)
rows = con.execute(
    "SELECT v.line_no, e.edge_kind, v.severity, v.disposition "
    "FROM violations v LEFT JOIN edges e ON v.edge_id = e.id "
    "WHERE v.file_path = ? ORDER BY v.line_no",
    (target,),
).fetchall()
print(f"File: {target}")
print(f"Total: {len(rows)}")
for ln, ek, sev, disp in rows:
    print(f"  L{ln:4d}  {sev:6s}  {ek:30s}  disp={disp}")
con.close()
