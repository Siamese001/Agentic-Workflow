"""Find files with hardcoded absolute paths and broad-catch antipatterns suitable for safe burndown."""

# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"

import sqlite3

c = sqlite3.connect(r"artifacts/adg/adg_indexed_04252026_0521.sqlite")
cur = c.cursor()

print("=== HARDCODED ABSOLUTE PATHS (C:\\Git, C:/Git, D:\\) ===")
cur.execute("""
    SELECT file_path, line_no, evidence FROM violations
    WHERE evidence LIKE 'C:%' OR evidence LIKE 'D:%'
    ORDER BY file_path LIMIT 100
""")
for r in cur.fetchall():
    print(r)

print()
print("=== TOP NON-TEST FILES WITH BROAD CATCHES (Exception/AttributeError/OSError) ===")
cur.execute("""
    SELECT file_path, COUNT(*) as cnt FROM violations
    WHERE category='antipattern'
      AND evidence IN ('Exception', 'AttributeError', 'OSError', 'ValueError', 'KeyError', 'ImportError')
      AND file_path NOT LIKE 'tests/%'
      AND file_path NOT LIKE '%test_%'
      AND file_path NOT LIKE '%conftest%'
    GROUP BY file_path
    HAVING cnt >= 5
    ORDER BY cnt DESC LIMIT 50
""")
for r in cur.fetchall():
    print(r)

print()
print("=== L2->L0 SC-1 VIOLATIONS DETAIL ===")
cur.execute("""
    SELECT file_path, line_no, evidence FROM violations
    WHERE category='SC-1'
""")
for r in cur.fetchall():
    print(r)
