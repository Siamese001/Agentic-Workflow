# W6 ADG consumer mode declaration (per .codex/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"

import sqlite3
c = sqlite3.connect('artifacts/adg/adg_indexed_04252026_0521.sqlite')
cur = c.cursor()
cur.execute("SELECT id, severity, evidence, file_path, line_no FROM violations WHERE severity IN ('HIGH','CRITICAL','P0') AND disposition='untriaged'")
for r in cur.fetchall():
    print(r)
