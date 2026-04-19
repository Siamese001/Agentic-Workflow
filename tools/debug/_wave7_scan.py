import sqlite3
from pathlib import Path

db = r"artifacts/adg/adg_indexed_04192026_1246.sqlite"
c = sqlite3.connect(db)

rows = c.execute(
    "SELECT file_path, COUNT(*) AS n FROM violations "
    "WHERE severity='HIGH' AND category='antipattern' "
    "GROUP BY file_path ORDER BY n DESC LIMIT 12"
).fetchall()

print("Top 12:")
for path, n in rows:
    print(f"  {n:3d}  {path}")

TOP = [p for p, _ in rows[:8]]
for p in TOP:
    detail = c.execute(
        "SELECT line_no, violation_class FROM violations "
        "WHERE severity='HIGH' AND category='antipattern' AND file_path=? "
        "ORDER BY line_no",
        (p,),
    ).fetchall()
    print(f"\n=== {p} ({len(detail)} rows) ===")
    src = Path(p).read_text(encoding="utf-8", errors="ignore").splitlines()
    for line_no, vc in detail:
        print(f"  L{line_no} [{vc}]")
        start = max(0, line_no - 2)
        end = min(len(src), line_no + 3)
        for i in range(start, end):
            marker = ">>>" if (i + 1) == line_no else "   "
            print(f"    {marker} {i + 1}: {src[i][:130]}")
