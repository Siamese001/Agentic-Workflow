# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"

import sqlite3

con = sqlite3.connect("artifacts/adg/adg_indexed_04242026_0558_test.sqlite")
for r in con.execute("SELECT sql FROM sqlite_master WHERE name='violations'"):
    print(r[0])
