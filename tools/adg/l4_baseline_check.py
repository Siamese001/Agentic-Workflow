"""L4 Memory Authority baseline check - writes_through vs writes_to."""
import pathlib
import sqlite3
import sys

db = pathlib.Path(r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03162026_1534.sqlite")
if not db.exists():
    # Find latest
    adg_dir = pathlib.Path(r"C:\Git\Agentic-Workflow\artifacts\adg")
    dbs = sorted(adg_dir.glob("adg_indexed_*.sqlite"))
    if not dbs:
        print("No ADG SQLite found"); sys.exit(1)
    db = dbs[-1]

print(f"Using: {db.name}")
conn = sqlite3.connect(str(db))

# Baseline counts
rows = conn.execute(
    "SELECT relation_type, COUNT(*) FROM edges "
    "WHERE relation_type IN ('writes_to','writes_through') "
    "GROUP BY relation_type",
).fetchall()
counts = dict(rows)
wt = counts.get("writes_to", 0)
wth = counts.get("writes_through", 0)
ratio = wth / wt if wt > 0 else 0
target = int(wt * 0.90)
gap = max(0, target - wth)

print(f"writes_to      = {wt:,}")
print(f"writes_through = {wth:,}")
print(f"current_ratio  = {ratio:.1%}")
print("target_ratio   = 90.0%")
print(f"target_count   = {target:,}")
print(f"gap_remaining  = {gap:,}")

# Top modules with writes_to but missing/low writes_through
print("\n--- Top apps_* modules with writes_to but no writes_through ---")
rows2 = conn.execute("""
    SELECT e.source_file,
           SUM(CASE WHEN e.relation_type='writes_to' THEN 1 ELSE 0 END) as wt_count,
           SUM(CASE WHEN e.relation_type='writes_through' THEN 1 ELSE 0 END) as wth_count
    FROM edges e
    WHERE e.relation_type IN ('writes_to','writes_through')
      AND e.source_file LIKE 'apps_%'
    GROUP BY e.source_file
    HAVING wt_count > 0
    ORDER BY wt_count DESC
    LIMIT 50
""").fetchall()

for sf, wt_c, wth_c in rows2:
    marker = " *** NO writes_through" if wth_c == 0 else ""
    print(f"  {sf}: writes_to={wt_c}, writes_through={wth_c}{marker}")

# Also show total by top-level dir
print("\n--- writes_to / writes_through by top-level directory ---")
rows3 = conn.execute("""
    SELECT
        CASE
            WHEN source_file LIKE 'apps_%' THEN substr(source_file, 1, instr(source_file, '/') - 1)
            WHEN source_file LIKE 'tools/%' THEN 'tools'
            WHEN source_file LIKE 'ops_scripts/%' THEN 'ops_scripts'
            WHEN source_file LIKE 'agentic_core/%' THEN 'agentic_core'
            WHEN source_file LIKE 'tests/%' THEN 'tests'
            ELSE 'other'
        END as dir_group,
        relation_type,
        COUNT(*) as cnt
    FROM edges
    WHERE relation_type IN ('writes_to','writes_through')
    GROUP BY dir_group, relation_type
    ORDER BY dir_group, relation_type
""").fetchall()

from collections import defaultdict

grouped = defaultdict(dict)
for dg, rt, cnt in rows3:
    grouped[dg][rt] = cnt

for dg in sorted(grouped.keys()):
    wt_c = grouped[dg].get("writes_to", 0)
    wth_c = grouped[dg].get("writes_through", 0)
    r = wth_c / wt_c if wt_c > 0 else 0
    print(f"  {dg}: writes_to={wt_c}, writes_through={wth_c}, ratio={r:.1%}")

conn.close()
