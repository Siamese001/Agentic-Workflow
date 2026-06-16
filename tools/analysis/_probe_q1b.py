# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"

import sqlite3
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]
DB = str(REPO_ROOT / "artifacts" / "adg" / "adg_indexed_04252026_0521.sqlite")
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = con.cursor()

# Check how many symbols exist with non-empty layer
count = cur.execute(
    "SELECT COUNT(*) FROM nodes WHERE entity_type='symbol' AND layer IS NOT NULL AND layer != ''"
).fetchone()[0]
print(f"Total symbols with non-empty layer: {count}")

# Check how many match ADG::Symbol::
count2 = cur.execute(
    "SELECT COUNT(*) FROM nodes WHERE entity_type='symbol' AND adg_name LIKE 'ADG::Symbol::%' AND layer IS NOT NULL AND layer != ''"
).fetchone()[0]
print(f"Symbols matching ADG::Symbol::% with layer: {count2}")

# Check how many have :: in the part after ADG::Symbol::
count3 = cur.execute(
    "SELECT COUNT(*) FROM nodes WHERE entity_type='symbol' "
    "AND adg_name LIKE 'ADG::Symbol::%' AND layer IS NOT NULL AND layer != '' "
    "AND adg_name NOT LIKE '%::*'"
).fetchone()[0]
print(f"Symbols NOT matching %::* with layer: {count3}")

# Show short_name extraction for a few with ::
print("\n=== Short name extraction (with :: in name) ===")
for r in cur.execute(
    "SELECT adg_name, "
    "  CASE WHEN instr(substr(adg_name, 14), '::') > 0 "
    "    THEN substr(substr(adg_name, 14), instr(substr(adg_name, 14), '::') + 2) "
    "    ELSE substr(adg_name, 14) END AS short_name "
    "FROM nodes WHERE entity_type='symbol' AND adg_name LIKE 'ADG::Symbol::%' "
    "AND layer IS NOT NULL AND layer != '' "
    "LIMIT 15"
).fetchall():
    print(r)

# Try grouping by the extracted short name
print("\n=== Top duplicate short names (>=3 files) ===")
for r in cur.execute(
    "SELECT CASE WHEN instr(substr(adg_name, 14), '::') > 0 "
    "    THEN substr(substr(adg_name, 14), instr(substr(adg_name, 14), '::') + 2) "
    "    ELSE substr(adg_name, 14) END AS short_name, "
    "  COUNT(DISTINCT resolved_path) AS file_count, "
    "  COUNT(DISTINCT layer) AS layer_count, "
    "  GROUP_CONCAT(DISTINCT layer) AS layers "
    "FROM nodes WHERE entity_type='symbol' AND adg_name LIKE 'ADG::Symbol::%' "
    "AND layer IS NOT NULL AND layer != '' "
    "GROUP BY short_name "
    "HAVING COUNT(DISTINCT resolved_path) >= 3 "
    "ORDER BY file_count DESC LIMIT 20"
).fetchall():
    print(r)

con.close()
