"""L4 Phase 2 — reads_from / reads_through baseline check."""
import sqlite3
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"C:\Git\Agentic-Workflow")
ADG_DIR = ROOT / "artifacts" / "adg"
db = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"))[-1]
print(f"Using: {db.name}")
conn = sqlite3.connect(str(db))

# Verification SQL
rows = conn.execute("""
    SELECT relation_type, COUNT(*)
    FROM edges
    WHERE relation_type IN ('reads_from','reads_through')
    GROUP BY relation_type
""").fetchall()
counts = dict(rows)
rf = counts.get('reads_from', 0)
rt = counts.get('reads_through', 0)
ratio = rt / rf if rf > 0 else 0
target = -(-int(rf * 0.90) // 1)  # ceil
gap = max(0, target - rt)
uncovered = rf - rt

print(f"reads_from     = {rf:,}")
print(f"reads_through  = {rt:,}")
print(f"current_ratio  = {ratio:.1%}")
print("target_ratio   = 90.0%")
print(f"target_count   = {target:,}")
print(f"gap_remaining  = {gap:,}")
print(f"uncovered_reads= {uncovered:,}")

# Uncovered reads count
uncovered_count = conn.execute("""
    SELECT COUNT(*)
    FROM edges r
    LEFT JOIN edges g
      ON r.source_file = g.source_file
     AND g.relation_type = 'reads_through'
    WHERE r.relation_type = 'reads_from'
      AND g.source_file IS NULL
""").fetchone()[0]
print(f"\nModules with reads_from but zero reads_through: {uncovered_count}")

# Per-directory breakdown
dir_rows = conn.execute("""
    SELECT e.source_file,
           SUM(CASE WHEN e.relation_type='reads_from' THEN 1 ELSE 0 END) as rf,
           SUM(CASE WHEN e.relation_type='reads_through' THEN 1 ELSE 0 END) as rt
    FROM edges e
    WHERE e.relation_type IN ('reads_from','reads_through')
    GROUP BY e.source_file
    HAVING rf > 0
""").fetchall()

dir_gaps = defaultdict(lambda: {"modules": 0, "rf": 0, "rt": 0, "gap": 0})
for source_file, rf_m, rt_m in dir_rows:
    parts = source_file.split("/")
    if source_file.startswith("tests/"):
        dg = "tests"
    elif source_file.startswith("agentic_core/"):
        dg = "agentic_core/" + parts[1] if len(parts) > 1 else "agentic_core"
    elif source_file.startswith("ops_scripts/"):
        dg = "ops_scripts"
    elif source_file.startswith("tools/"):
        if len(parts) > 1 and parts[1] == "evidence":
            dg = "tools/evidence"
        else:
            dg = "tools"
    elif source_file.startswith("apps_"):
        dg = parts[0]
    else:
        dg = "other"

    gap_m = max(0, rf_m - rt_m)
    if gap_m > 0:
        dir_gaps[dg]["modules"] += 1
        dir_gaps[dg]["rf"] += rf_m
        dir_gaps[dg]["rt"] += rt_m
        dir_gaps[dg]["gap"] += gap_m

print(f"\n{'Directory':<40} {'Modules':>8} {'reads_from':>11} {'reads_through':>14} {'Gap':>8}")
print("-" * 85)
for dg in sorted(dir_gaps.keys(), key=lambda x: -dir_gaps[x]["gap"]):
    d = dir_gaps[dg]
    print(f"  {dg:<38} {d['modules']:>8} {d['rf']:>11} {d['rt']:>14} {d['gap']:>8}")

conn.close()
