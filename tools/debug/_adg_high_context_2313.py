import sqlite3
from pathlib import Path

DB = "artifacts/adg/adg_indexed_04232026_2313.sqlite"
c = sqlite3.connect(DB).cursor()
rows = c.execute(
    "SELECT v.id, v.file_path, v.line_no, v.evidence, e.edge_kind "
    "FROM violations v LEFT JOIN edges e ON v.edge_id = e.id "
    "WHERE v.severity='HIGH'"
).fetchall()
for vid, fp, ln, ev, ek in rows:
    print(f"\n--- id={vid} {fp}:{ln} edge_kind={ek} evidence={ev} ---")
    p = Path(fp)
    if not p.exists():
        print("  (file missing)")
        continue
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    lo, hi = max(1, ln - 2), min(len(lines), ln + 2)
    for i in range(lo, hi + 1):
        marker = ">>" if i == ln else "  "
        print(f"  {marker} {i:>5}: {lines[i - 1]}")
