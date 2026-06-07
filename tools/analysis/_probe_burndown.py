# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"

import sqlite3
c = sqlite3.connect(r"artifacts/adg/adg_indexed_04252026_0521.sqlite")
cur = c.cursor()

print("=== HIGH-SEVERITY VIOLATIONS ===")
cur.execute("SELECT category, evidence, file_path, line_no, severity FROM violations WHERE severity IN ('CRITICAL','HIGH') OR category='SC-1' LIMIT 20")
for r in cur.fetchall():
    print(r)

print()
print("=== TOP 25 ANTIPATTERN EVIDENCE ===")
cur.execute("SELECT evidence, COUNT(*) FROM violations WHERE category='antipattern' GROUP BY evidence ORDER BY 2 DESC LIMIT 25")
for r in cur.fetchall():
    print(r)

print()
print("=== TOP FILES BY VIOLATION COUNT ===")
cur.execute("SELECT file_path, COUNT(*) FROM violations WHERE category='antipattern' GROUP BY file_path ORDER BY 2 DESC LIMIT 25")
for r in cur.fetchall():
    print(r)
