import sqlite3
import glob
from agentic_core.L0_routing.config.path_constants import ADG_ARTIFACTS_DIR
f"{ADG_ARTIFACTS_DIR}/*.sqlite"
db = sorted(glob.glob(f"{ADG_ARTIFACTS_DIR}/*.sqlite"))[-1]
print("DB:", db)
con = sqlite3.connect(db)
cur = con.cursor()

cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type = 'gates_promotion'")
print("gates_promotion edge count:", cur.fetchone()[0])

cur.execute(
    "SELECT relation_type, source_file, symbol, line_no FROM edges WHERE relation_type = 'gates_promotion'"
)
for row in cur.fetchall():
    print(" ", row)

print()
cur.execute(
    "SELECT COUNT(*) FROM edges"
    " WHERE source_file = 'agentic_core/runtime/engine/eval_spine.py'"
    "   AND symbol LIKE '%gates_promotion%'"
)
print("eval_spine gates_promotion symbol count:", cur.fetchone()[0])

cur.execute(
    "SELECT source_file, symbol, relation_type, line_no FROM edges"
    " WHERE source_file = 'agentic_core/runtime/engine/eval_spine.py'"
    "   AND symbol LIKE '%emit%'"
)
print("\nAll emit-related edges from eval_spine.py:")
for row in cur.fetchall():
    print(" ", row)

con.close()
