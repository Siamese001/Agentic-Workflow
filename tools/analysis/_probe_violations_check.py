# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"

import sqlite3
c = sqlite3.connect('artifacts/adg/adg_indexed_04252026_0521.sqlite')
cur = c.cursor()
cur.execute("SELECT COUNT(*) FROM violations WHERE severity IN ('HIGH','CRITICAL','P0') AND disposition='untriaged'")
print("hard-block rows:", cur.fetchone()[0])
cur.execute("SELECT severity, COUNT(*) FROM violations WHERE disposition='untriaged' GROUP BY severity")
for r in cur.fetchall():
    print(r)
print()
cur.execute("SELECT severity, COUNT(*) FROM violations GROUP BY severity")
print("ALL violations:")
for r in cur.fetchall():
    print(r)
print()
cur.execute("SELECT COUNT(*) FROM violations")
print("TOTAL violations:", cur.fetchone()[0])
print()
# Maybe disposition column has different values
cur.execute("SELECT disposition, COUNT(*) FROM violations GROUP BY disposition")
print("By disposition:")
for r in cur.fetchall():
    print(r)
