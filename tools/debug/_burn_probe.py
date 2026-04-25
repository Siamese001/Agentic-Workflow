"""Probe each HIGH/CRITICAL antipattern with full source context for bulk burn."""

import sqlite3
from pathlib import Path

p = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda x: x.stat().st_mtime)[-1]
c = sqlite3.connect(p)
rows = c.execute(
    """
    SELECT v.id, v.severity, e.edge_kind, e.symbol, v.file_path, v.line_no
    FROM violations v JOIN edges e ON v.edge_id = e.id
    WHERE v.severity IN ('HIGH','CRITICAL') AND v.category='antipattern'
    ORDER BY v.file_path, v.line_no
    """
).fetchall()
print(f"snap: {p.name}  ({len(rows)} rows)\n")
for vid, sev, kind, sym, fp, ln in rows:
    src = Path(fp).read_text(encoding="utf-8", errors="replace").splitlines()
    print(f"[{sev}] {kind} evidence={sym!r}  {fp}:{ln}")
    lo, hi = max(0, ln - 3), min(len(src), ln + 3)
    for i in range(lo, hi):
        marker = " >>>" if i + 1 == ln else "    "
        print(f"  {marker} {i + 1:5}: {src[i][:130]}")
    print()
