import sqlite3

db = sqlite3.connect('artifacts/adg/adg_indexed_04192026_1616.sqlite')
cols = [r[1] for r in db.execute("PRAGMA table_info(violations)").fetchall()]
print("violations cols:", cols)
print("distinct severities:", db.execute("SELECT DISTINCT severity FROM violations").fetchall())
print("distinct dispositions:", db.execute("SELECT DISTINCT disposition FROM violations").fetchall())
print("counts by severity:", db.execute("SELECT severity, COUNT(*) FROM violations GROUP BY severity").fetchall())
rows = db.execute(
    "SELECT file_path, line_no, category, evidence FROM violations WHERE severity='HIGH' ORDER BY file_path, line_no"
).fetchall()
print(f"\nP1 (HIGH) violations ({len(rows)}):")
for r in rows:
    print(f"  {r[0]}:{r[1]}  [{r[2]}]  {r[3]}")
db.close()
