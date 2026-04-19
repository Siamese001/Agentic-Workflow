"""
ADG-first P1 HIGH hotspot scan.
Queries violations table for open P1 sites, groups by file,
computes blast radius (fan-in) from edges table, and ranks by
impact = count * (1 + log10(1 + fan_in)).
"""

import sqlite3
import math
import json

DB = r"artifacts/adg/adg_indexed_04192026_1335.sqlite"
conn = sqlite3.connect(DB)
cur = conn.cursor()

# 1. Distinct severities and disposition values
cur.execute("SELECT DISTINCT severity, disposition FROM violations ORDER BY severity, disposition")
print("SEVERITY/DISPOSITION combos:", cur.fetchall())

# 2. Distinct categories (antipattern kinds)
cur.execute("SELECT DISTINCT category, COUNT(*) as n FROM violations GROUP BY category ORDER BY n DESC")
print("\nCATEGORIES:")
for row in cur.fetchall():
    print(f"  {row[0]:50s}  {row[1]}")

# 3. P1 HIGH open sites by file with kind breakdown
cur.execute("""
    SELECT file_path,
           COUNT(*) as total,
           SUM(CASE WHEN category='broad_exception_catch'    THEN 1 ELSE 0 END) as broad,
           SUM(CASE WHEN category='silent_exception_swallow' THEN 1 ELSE 0 END) as silent,
           SUM(CASE WHEN category='log_and_swallow'          THEN 1 ELSE 0 END) as log_sw,
           SUM(CASE WHEN category='return_none_swallow'      THEN 1 ELSE 0 END) as ret_none
    FROM violations
    WHERE severity='HIGH'
      AND (disposition IS NULL OR disposition NOT IN ('exempted','guardian_exempted','waived'))
    GROUP BY file_path
    ORDER BY total DESC
    LIMIT 60
""")
rows = cur.fetchall()


# 4. Fan-in per file path (incoming import edges)
def fan_in(file_path):
    cur2 = conn.cursor()
    cur2.execute(
        """
        SELECT COUNT(DISTINCT src_id) FROM edges
        WHERE relation_type='imports'
          AND source_file LIKE ?
    """,
        (f"%{file_path.replace('agentic_core/', '')}%",),
    )
    r = cur2.fetchone()
    return r[0] if r else 0


print("\nP1 HIGH HOTSPOTS (open, ranked by impact = count * (1 + log10(1+fan_in))):")
print(
    f"{'rank':>4}  {'total':>5}  {'broad':>5}  {'silent':>6}  {'log_sw':>6}  {'ret_none':>8}  {'fan_in':>6}  {'impact':>7}  file"
)
print("-" * 130)

ranked = []
for row in rows:
    fp, total, broad, silent, log_sw, ret_none = row
    fi = fan_in(fp)
    impact = total * (1 + math.log10(1 + fi))
    ranked.append((impact, total, broad, silent, log_sw, ret_none, fi, fp))

ranked.sort(reverse=True)
for i, (impact, total, broad, silent, log_sw, ret_none, fi, fp) in enumerate(ranked, 1):
    print(
        f"{i:>4}  {total:>5}  {broad:>5}  {silent:>6}  {log_sw:>6}  {ret_none:>8}  {fi:>6}  {impact:>7.1f}  {fp}"
    )

# 5. Summary totals
cur.execute("""
    SELECT severity,
           COUNT(*) as total,
           SUM(CASE WHEN disposition IN ('exempted','guardian_exempted','waived') THEN 1 ELSE 0 END) as exempted,
           SUM(CASE WHEN disposition IS NULL OR disposition NOT IN ('exempted','guardian_exempted','waived') THEN 1 ELSE 0 END) as open
    FROM violations
    GROUP BY severity
    ORDER BY severity
""")
print("\nSUMMARY BY SEVERITY:")
for row in cur.fetchall():
    print(f"  severity={row[0]:5s}  total={row[1]:5d}  exempted={row[2]:5d}  open={row[3]:5d}")

conn.close()
