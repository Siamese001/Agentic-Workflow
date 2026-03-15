"""Quick baseline counts for P0/L5."""

import glob
import os
import sqlite3

os.chdir(r"C:\Git\Agentic-Workflow")
dbs = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))
db = dbs[-1]
print(f"DB: {db}")
conn = sqlite3.connect(db)
c = conn.cursor()
NON_TEST = (
    "AND source_file NOT LIKE '%test%' AND source_file NOT LIKE '%tests%' "
    "AND source_file NOT LIKE '%spec%' AND source_file NOT LIKE '%fixture%' "
    "AND source_file NOT LIKE '%mock%'"
)
for et in [
    "reads_policy_state",
    "applies_guardrail",
    "references_policy_hash",
    "validated_by_safety_plane",
    "requires_human_review",
    "escalates_to_human",
]:
    c.execute(f"SELECT COUNT(*) FROM edges WHERE relation_type=? {NON_TEST}", (et,))
    rt = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (et,))
    tot = c.fetchone()[0]
    print(f"  {et:<42} runtime={rt:>5}  total={tot:>5}")
conn.close()
