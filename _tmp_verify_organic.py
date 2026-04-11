import sqlite3
from pathlib import Path

DB = Path(".windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite")
conn = sqlite3.connect(str(DB))

rows = conn.execute(
    "SELECT decision_id, decision_type, normalized_intent, selected_option_id, created_at "
    "FROM decisions ORDER BY created_at DESC LIMIT 3"
).fetchall()

print(f"Latest decisions (most recent first):")
for r in rows:
    did, dtype, intent, sel, ts = r
    source = "organic" if intent and intent.startswith(".windsurf") else "backfill"
    print(f"  [{source}] {did}  {dtype}")
    print(f"           intent : {repr(intent[:80])}")
    print(f"           selected: {repr((sel or '')[:80])}")
    print(f"           at      : {ts}")
    print()

total = conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
organic = conn.execute("SELECT COUNT(*) FROM decisions WHERE normalized_intent LIKE '.windsurf%'").fetchone()[
    0
]
print(f"Total: {total}  |  Backfill: {total - organic}  |  Organic: {organic}")
conn.close()
