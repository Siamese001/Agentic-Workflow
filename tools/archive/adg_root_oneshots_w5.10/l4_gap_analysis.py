"""L4 gap analysis — count remaining modules needing writes_through."""

import re
import sqlite3
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"C:\Git\Agentic-Workflow")
ADG_DIR = ROOT / "artifacts" / "adg"
db = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"))[-1]
print(f"Using: {db.name}")
conn = sqlite3.connect(str(db))

# Get ALL modules with writes_to, check on-disk _emit_writes_through count
rows = conn.execute("""
    SELECT e.source_file,
           SUM(CASE WHEN e.relation_type='writes_to' THEN 1 ELSE 0 END) as wt,
           SUM(CASE WHEN e.relation_type='writes_through' THEN 1 ELSE 0 END) as wth
    FROM edges e
    WHERE e.relation_type IN ('writes_to','writes_through')
    GROUP BY e.source_file
    HAVING wt > 0
    ORDER BY (wt - wth) DESC
""").fetchall()

total_wt = 0
total_wth_db = 0
total_wth_disk = 0
total_gap = 0
uncovered_count = 0
dir_gaps = defaultdict(lambda: {"modules": 0, "gap": 0, "wt": 0})

for source_file, wt, wth_db in rows:
    total_wt += wt
    total_wth_db += wth_db
    fp = ROOT / source_file
    if fp.exists():
        text = fp.read_text(encoding="utf-8", errors="replace")
        disk_calls = len(re.findall(r"_emit_writes_through\(", text))
    else:
        disk_calls = wth_db
    total_wth_disk += disk_calls
    gap = max(0, wt - disk_calls)
    total_gap += gap

    # Determine directory group
    parts = source_file.split("/")
    if source_file.startswith("tests/"):
        dg = "tests"
    elif source_file.startswith("agentic_core/"):
        dg = "agentic_core/" + parts[1] if len(parts) > 1 else "agentic_core"
    elif source_file.startswith("ops_scripts/"):
        dg = "ops_scripts"
    elif source_file.startswith("tools/"):
        dg = "tools/" + parts[1] if len(parts) > 1 else "tools"
    elif source_file.startswith("apps_"):
        dg = parts[0]
    else:
        dg = "other"

    if gap > 0:
        uncovered_count += 1
        dir_gaps[dg]["modules"] += 1
        dir_gaps[dg]["gap"] += gap
        dir_gaps[dg]["wt"] += wt

print(f"\nTotal modules with writes_to: {len(rows)}")
print(f"Total writes_to (ADG):       {total_wt:,}")
print(f"Total writes_through (ADG):  {total_wth_db:,}")
print(f"Total writes_through (disk): {total_wth_disk:,}")
print(f"Total remaining gap:         {total_gap:,}")
print(f"Modules still needing work:  {uncovered_count}")

disk_ratio = total_wth_disk / total_wt if total_wt > 0 else 0
target = int(total_wt * 0.90)
print(f"\nDisk-based ratio:  {disk_ratio:.1%}")
print(f"Target (90%):      {target:,}")
print(f"Gap to target:     {max(0, target - total_wth_disk):,}")

print(f"\n{'Directory':<40} {'Modules':>8} {'Gap':>8} {'writes_to':>10}")
print("-" * 70)
for dg in sorted(dir_gaps.keys(), key=lambda x: -dir_gaps[x]["gap"]):
    d = dir_gaps[dg]
    print(f"  {dg:<38} {d['modules']:>8} {d['gap']:>8} {d['wt']:>10}")

conn.close()
