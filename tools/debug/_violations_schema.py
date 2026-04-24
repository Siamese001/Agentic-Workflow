import sqlite3
from pathlib import Path
from collections import Counter
p = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda x: x.stat().st_mtime)[-1]
c = sqlite3.connect(p)
cols = [r[1] for r in c.execute("PRAGMA table_info(violations)")]
print(f"violations cols: {cols}")
row = c.execute("SELECT * FROM violations LIMIT 1").fetchone()
print(f"sample: {row}\n")

# severity breakdown
print("=== violations by severity ===")
for r in c.execute("SELECT severity, COUNT(*) FROM violations GROUP BY severity ORDER BY COUNT(*) DESC"):
    print(f"  {r[0]:20s} {r[1]}")

print("\n=== violations by category ===")
for r in c.execute("SELECT category, COUNT(*) FROM violations GROUP BY category ORDER BY COUNT(*) DESC LIMIT 25"):
    print(f"  {str(r[0]):40s} {r[1]}")

print("\n=== violations severity x category (top 20) ===")
for r in c.execute("""
    SELECT severity, category, COUNT(*) AS n
    FROM violations GROUP BY severity, category
    ORDER BY n DESC LIMIT 20
"""):
    print(f"  [{r[0]:10s}] {str(r[1]):40s} {r[2]}")
