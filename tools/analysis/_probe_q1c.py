# W6 ADG consumer mode declaration (per .windsurf/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"

import sqlite3
DB = r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_04252026_0521.sqlite"
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = con.cursor()

# Use the last component after the last dot as the short name
# SQLite doesn't have strrchr, so use a recursive approach or reverse trick
print("=== Top duplicate short names (last dot component, >=3 files) ===")
for r in cur.execute(
    "SELECT replace(substr(adg_name, 14), 'agentic_core.', '') AS base_name, "
    "  CASE WHEN instr(reverse(substr(adg_name, 14)), '.') > 0 "
    "    THEN substr(substr(adg_name, 14), "
    "      length(substr(adg_name, 14)) - instr(reverse(substr(adg_name, 14)), '.') + 2) "
    "    ELSE substr(adg_name, 14) END AS short_name, "
    "  COUNT(DISTINCT resolved_path) AS file_count, "
    "  COUNT(DISTINCT layer) AS layer_count, "
    "  GROUP_CONCAT(DISTINCT layer) AS layers "
    "FROM nodes WHERE entity_type='symbol' AND adg_name LIKE 'ADG::Symbol::%' "
    "AND layer IS NOT NULL AND layer != '' "
    "AND adg_name NOT LIKE '%.WindsurfMCP%' "  # exclude MCP artifacts
    "GROUP BY short_name "
    "HAVING COUNT(DISTINCT resolved_path) >= 3 "
    "ORDER BY file_count DESC LIMIT 20"
).fetchall():
    print(r)

con.close()
