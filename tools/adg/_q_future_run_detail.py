# W6 ADG consumer mode declaration (per .codex/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
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
    "SELECT e.relation_type, e.source_file, e.symbol"
    " FROM edges e"
    " WHERE e.relation_type IN ('promotes_future_run_change','gates_promotion','builds_dpo_batch','commits_optimization')"
    " ORDER BY e.relation_type, e.source_file"
)
rows = cur.fetchall()
con.close()

print(f"\n  {'relation_type':<30} {'source_file':<65} {'symbol':<40}")
print("  " + "-" * 140)
for rel, sf, sym in rows:
    print(f"  {rel:<30} {sf:<65} {sym:<40}")
