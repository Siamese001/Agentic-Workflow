"""Inspect violations row schema to understand evidence column semantics."""
import sqlite3, glob, os
latest = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)[-1]
c = sqlite3.connect(latest)
cur = c.cursor()

# Sample rows for NOTION_API_VERSION
cur.execute("SELECT * FROM violations WHERE evidence LIKE '%NOTION_API_VERSION%' LIMIT 5")
cols = [d[0] for d in cur.description]
print("Columns:", cols)
print()
for row in cur.fetchall():
    for col, val in zip(cols, row):
        print(f"  {col} = {val}")
    print()

# Now check whether '2025-09-03' literal still appears in file evidence
print("=" * 60)
print("Rows with '2025-09-03' literal:")
cur.execute("SELECT file_path, line_no, evidence, category FROM violations WHERE evidence LIKE '%2025-09-03%' LIMIT 20")
for fp, ln, ev, cat in cur.fetchall():
    print(f"  [{cat}] {fp}:{ln}  ::  {ev[:80]}")

print()
print("=" * 60)
print("Rows with 'aa8d2507' (Wave/Phase DB ID literal) NOT in allowlist:")
cur.execute("SELECT file_path, line_no, evidence, category FROM violations WHERE evidence LIKE '%aa8d2507%' AND file_path NOT LIKE 'tests/%'")
for fp, ln, ev, cat in cur.fetchall():
    print(f"  [{cat}] {fp}:{ln}  ::  {ev[:80]}")
