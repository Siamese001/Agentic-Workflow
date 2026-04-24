import glob
import os
import sqlite3
from pathlib import Path

files = sorted(glob.glob('artifacts/adg/adg_indexed_*.sqlite'), key=os.path.getmtime)
latest = files[-1]
print(f"LATEST: {latest}")
print(f"prior:  {files[-2] if len(files) > 1 else '(none)'}")

c = sqlite3.connect(latest).cursor()

rows = c.execute(
    "SELECT disposition, COUNT(*) FROM violations WHERE category='antipattern' "
    "GROUP BY disposition ORDER BY COUNT(*) DESC"
).fetchall()
print("\nAntipattern dispositions:")
for d, n in rows:
    print(f"  {n:>6}  {d}")

print("\nHIGH severity rows:")
rows = c.execute(
    "SELECT id, file_path, disposition, substr(disposition_source,1,80), severity "
    "FROM violations WHERE severity='HIGH'"
).fetchall()
for r in rows:
    print(f"  {r}")

# Total
n = c.execute("SELECT COUNT(*) FROM violations WHERE category='antipattern'").fetchone()[0]
print(f"\nTotal antipattern violations: {n}")

# Guardian recognition score
approved = c.execute(
    "SELECT COUNT(*) FROM violations WHERE category='antipattern' AND disposition='approved'"
).fetchone()[0]
print(f"Approved (guardian-matched): {approved}")
