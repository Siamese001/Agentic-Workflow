import sqlite3, glob, os
from pathlib import Path
snaps = sorted(glob.glob('artifacts/adg/adg_indexed_*.sqlite'), key=os.path.getmtime)
snap = snaps[-1]
print(f"snapshot: {Path(snap).name}")
c = sqlite3.connect(snap).cursor()
c.execute("SELECT COUNT(*) FROM violations WHERE severity='MEDIUM' AND category='antipattern'")
print("gate query MEDIUM+antipattern:", c.fetchone()[0])
print()
for r in c.execute("SELECT severity, category, COUNT(*) FROM violations GROUP BY 1,2 ORDER BY 3 DESC LIMIT 15"):
    print(r)
print()
print("=== CRITICAL violates ===")
for r in c.execute("SELECT file_path, line_no, evidence, disposition FROM violations WHERE severity='CRITICAL' AND category='violates' ORDER BY file_path, line_no"):
    print(f"  {r[0]}:{r[1]}  ev={r[2]}  disp={r[3]}")
