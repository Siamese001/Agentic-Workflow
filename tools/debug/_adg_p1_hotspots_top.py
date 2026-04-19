"""ADG-first P1 HIGH hotspot scan — top results only."""

import sqlite3
import math

DB = r"artifacts/adg/adg_indexed_04192026_1335.sqlite"
conn = sqlite3.connect(DB)
cur = conn.cursor()

# Distinct severities + dispositions
cur.execute(
    "SELECT DISTINCT severity, disposition, COUNT(*) as n FROM violations GROUP BY severity, disposition ORDER BY severity, n DESC"
)
print("=== SEVERITY / DISPOSITION ===")
for row in cur.fetchall():
    print(f"  {row[0]:8s}  disposition={str(row[1]):30s}  n={row[2]}")

# Distinct categories
cur.execute(
    "SELECT category, COUNT(*) as n FROM violations WHERE severity='HIGH' GROUP BY category ORDER BY n DESC"
)
print("\n=== P1 HIGH CATEGORIES ===")
for row in cur.fetchall():
    print(f"  {row[1]:5d}  {row[0]}")

# Top 20 hotspot files
cur.execute("""
    SELECT file_path,
           COUNT(*) as total,
           GROUP_CONCAT(DISTINCT category) as kinds,
           GROUP_CONCAT(line_no) as lines
    FROM violations
    WHERE severity='HIGH'
      AND (disposition IS NULL OR disposition NOT IN ('exempted','guardian_exempted','waived'))
    GROUP BY file_path
    ORDER BY total DESC
    LIMIT 20
""")
rows = cur.fetchall()

print("\n=== TOP 20 P1 HIGH HOTSPOT FILES (open) ===")
print(f"{'#':>3}  {'count':>5}  {'file':<80}  kinds")
print("-" * 120)
for i, (fp, total, kinds, lines) in enumerate(rows, 1):
    print(f"{i:>3}  {total:>5}  {fp:<80}  {kinds}")
    print(f"       lines: {lines}")

# Summary
cur.execute(
    "SELECT severity, COUNT(*) FROM violations WHERE disposition IS NULL OR disposition NOT IN ('exempted','guardian_exempted','waived') GROUP BY severity"
)
print("\n=== OPEN VIOLATIONS SUMMARY ===")
for row in cur.fetchall():
    print(f"  {row[0]:8s}  open={row[1]}")

conn.close()
