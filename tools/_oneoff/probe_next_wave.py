"""Probe next-wave candidates from latest ADG snapshot."""
import sqlite3
from pathlib import Path
from datetime import datetime


def _valid(p):
    try:
        datetime.strptime(p.stem.replace("adg_indexed_", ""), "%m%d%Y_%H%M")
        return True
    except ValueError:
        return False


valid = [p for p in Path("artifacts/adg").glob("adg_indexed_*.sqlite") if _valid(p)]
db = sorted(valid)[-1]
print(f"snap: {db.name}")
con = sqlite3.connect(db)

for sev in ["HIGH", "MEDIUM", "LOW"]:
    n = con.execute("SELECT COUNT(*) FROM violations WHERE severity=?", (sev,)).fetchone()[0]
    print(f"{sev}: {n}")

print("\n--- HIGH by category:")
for cat, n in con.execute(
    "SELECT category, COUNT(*) FROM violations WHERE severity='HIGH' GROUP BY category ORDER BY 2 DESC"
).fetchall():
    print(f"  {cat}: {n}")

print("\n--- HIGH antipattern by edge_kind (top 10):")
for ek, n in con.execute(
    "SELECT e.edge_kind, COUNT(*) FROM violations v "
    "JOIN edges e ON v.edge_id=e.id "
    "WHERE v.severity='HIGH' AND v.category='antipattern' "
    "GROUP BY e.edge_kind ORDER BY 2 DESC LIMIT 10"
).fetchall():
    print(f"  {ek}: {n}")

print("\n--- HIGH antipattern by disposition:")
for disp, n in con.execute(
    "SELECT disposition, COUNT(*) FROM violations "
    "WHERE severity='HIGH' AND category='antipattern' GROUP BY disposition"
).fetchall():
    print(f"  {disp}: {n}")

print("\n--- HIGH antipattern untriaged top 10 files:")
for fp, n in con.execute(
    "SELECT file_path, COUNT(*) FROM violations "
    "WHERE severity='HIGH' AND category='antipattern' AND disposition='untriaged' "
    "GROUP BY file_path ORDER BY 2 DESC LIMIT 10"
).fetchall():
    print(f"  {n:3d}  {fp}")

print("\n--- layer_violation HIGH top 10 files:")
for fp, n in con.execute(
    "SELECT file_path, COUNT(*) FROM violations "
    "WHERE severity='HIGH' AND category='layer_violation' "
    "GROUP BY file_path ORDER BY 2 DESC LIMIT 10"
).fetchall():
    print(f"  {n:3d}  {fp}")

con.close()
