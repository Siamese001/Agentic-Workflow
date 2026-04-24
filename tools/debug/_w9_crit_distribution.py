"""Show mv_path_criticality_rollup score distribution."""
import sqlite3
from pathlib import Path

snap = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime)[-1]
c = sqlite3.connect(snap)
print(f"snapshot: {snap.name}\n")
for lo, hi in [(5, 10), (10, 25), (25, 50), (50, 100), (100, 250), (250, 500), (500, 10000)]:
    n = c.execute(
        "SELECT COUNT(*) FROM mv_path_criticality_rollup "
        "WHERE violation_count > 0 AND criticality_score > ? AND criticality_score <= ?",
        (lo, hi),
    ).fetchone()[0]
    print(f"  {lo:4d} < score <= {hi:5d}  : {n}")
print("\ntop 10 by score:")
for r in c.execute(
    "SELECT resolved_path, layer, violation_count, fan_in, fan_out, criticality_score "
    "FROM mv_path_criticality_rollup WHERE violation_count > 0 "
    "ORDER BY criticality_score DESC LIMIT 10"
):
    print(f"  score={r[5]:7.1f}  v={r[2]:3d}  fan_in={r[3]:3d}  fan_out={r[4]:3d}  {r[1]:8s}  {r[0]}")
