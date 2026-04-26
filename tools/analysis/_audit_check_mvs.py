import sqlite3
import glob, os
latest = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)[-1]
print(f"Snapshot: {latest}")
c = sqlite3.connect(latest)
cur = c.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view') AND (name LIKE 'mv_%' OR name LIKE 'v_p%') ORDER BY name")
rows = [r[0] for r in cur.fetchall()]
print(f"\nFound {len(rows)} MV/P-view objects:")
for r in rows[:20]:
    print(f"  {r}")
if len(rows) > 20:
    print(f"  ... and {len(rows)-20} more")

print("\nAll tables:")
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
all_tables = [r[0] for r in cur.fetchall()]
print(f"  {len(all_tables)} tables total")

# Check baseline expectations
expected_mvs = ["mv_hotspot_centrality", "mv_dependency_cone_risk", "mv_path_criticality_rollup"]
for mv in expected_mvs:
    exists = mv in rows
    print(f"  {mv}: {'EXISTS' if exists else 'MISSING'}")
