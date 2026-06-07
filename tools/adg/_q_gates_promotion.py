# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"

import sqlite3
import glob
from agentic_core.L0_routing.config.path_constants import ADG_ARTIFACTS_DIR

f"{ADG_ARTIFACTS_DIR}/*.sqlite"
db = sorted(glob.glob(f"{ADG_ARTIFACTS_DIR}/*.sqlite"))[-1]
print("DB:", db)
con = sqlite3.connect(db)
cur = con.cursor()

cur.execute(
    "SELECT relation_type, source_file, symbol, line_no"
    " FROM edges"
    " WHERE symbol LIKE '%gates_promotion%' OR relation_type LIKE '%gates_promotion%'"
    " ORDER BY source_file"
)
rows = cur.fetchall()
print(f"\nFound {len(rows)} edges for gates_promotion:")
for row in rows:
    print(" ", row)

cur.execute("SELECT DISTINCT relation_type FROM edges WHERE source_file LIKE '%eval_spine%'")
print("\nAll relation_types from eval_spine.py:")
for row in cur.fetchall():
    print(" ", row[0])

con.close()
