import sqlite3
from pathlib import Path

c = sqlite3.connect(r"artifacts/adg/adg_indexed_04192026_1251.sqlite")
for p in [
    "system_learning/engines/hitl_decision_logger.py",
    "agentic_core/utils/ast_fuzzy_util.py",
    "agentic_core/tracing/engines/distributed_tracing_coordinator.py",
]:
    rows = c.execute(
        "SELECT line_no, violation_class FROM violations WHERE severity='HIGH' AND file_path=? ORDER BY line_no",
        (p,),
    ).fetchall()
    src = Path(p).read_text(encoding="utf-8", errors="ignore").splitlines()
    print(f"\n=== {p} ===")
    for line_no, vc in rows:
        print(f"  L{line_no} [{vc}]")
        for i in range(max(0, line_no - 2), min(len(src), line_no + 3)):
            print(f"    {'>>>' if i + 1 == line_no else '   '} {i + 1}: {src[i][:140]}")

# Also find top new offenders outside W7 scope
print("\n=== Top P1 files (post-W7) ===")
rows = c.execute(
    "SELECT file_path, COUNT(*) FROM violations WHERE severity='HIGH' AND category='antipattern' "
    "GROUP BY file_path ORDER BY COUNT(*) DESC LIMIT 10"
).fetchall()
for f, n in rows:
    print(f"  {n:3d}  {f}")
