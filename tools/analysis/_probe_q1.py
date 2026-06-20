# W6 ADG consumer mode declaration (per .codex/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"

import sqlite3
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]
DB = str(REPO_ROOT / "artifacts" / "adg" / "adg_indexed_04252026_0521.sqlite")
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = con.cursor()

print("=== Sample symbol names ===")
for r in cur.execute(
    "SELECT adg_name, layer FROM nodes "
    "WHERE entity_type = 'symbol' AND layer IS NOT NULL AND layer != '' "
    "LIMIT 10"
).fetchall():
    print(r)

# Test short name extraction
print("\n=== Short name extraction test ===")
for r in cur.execute(
    "SELECT adg_name, "
    "  substr(adg_name, instr(adg_name, '::') + 2) AS short_name "
    "FROM nodes WHERE entity_type = 'symbol' AND adg_name LIKE 'ADG::Symbol::%' "
    "LIMIT 10"
).fetchall():
    print(r)

# Try alternative: use last component after last dot
print("\n=== Alternative: last component ===")
for r in cur.execute(
    "SELECT adg_name, "
    "  replace(substr(adg_name, instr(adg_name, '::') + 2), 'agentic_core.', '') AS short_name "
    "FROM nodes WHERE entity_type = 'symbol' AND adg_name LIKE 'ADG::Symbol::%' "
    "LIMIT 10"
).fetchall():
    print(r)

con.close()
