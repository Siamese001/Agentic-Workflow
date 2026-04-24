"""Probe each HIGH violation — source text at exact line scanner reports."""
import sqlite3
from pathlib import Path
p = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda x: x.stat().st_mtime)[-1]
c = sqlite3.connect(p)
print(f"snap: {p.name}\n")
rows = c.execute("""
    SELECT v.id, v.severity, e.edge_kind, e.symbol, v.file_path, v.line_no, e.relation_type
    FROM violations v JOIN edges e ON v.edge_id = e.id
    WHERE v.severity IN ('HIGH', 'CRITICAL')
    ORDER BY v.file_path, v.line_no
""").fetchall()
for vid, sev, kind, sym, fp, ln, rel in rows:
    src = Path(fp).read_text(encoding="utf-8", errors="replace").splitlines()
    window = src[max(0, ln-3):ln+2]
    print(f"[{sev}] {kind} ({rel}) {fp}:{ln}  evidence={sym!r}")
    for i, line in enumerate(window, start=max(1, ln-2)):
        marker = " >>>" if i == ln else "    "
        print(f"  {marker} {i:5}: {line[:130]}")
    print()
