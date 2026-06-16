# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"

# Probe: Q6 using edges directly for fan-out layer mixing
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DB = str(REPO_ROOT / "artifacts" / "adg" / "adg_indexed_04252026_0521.sqlite")
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = con.cursor()

# Approach: aggregate edges by source file, count distinct callee layers
print("=== Top 20 source files by distinct callee layer count ===")
for r in cur.execute(
    "SELECT src_n.resolved_path AS caller_file, "
    "       src_n.layer AS caller_layer, "
    "       COUNT(DISTINCT e.dst_id) AS distinct_callees, "
    "       COUNT(DISTINCT dst_n.layer) AS callee_layer_count, "
    "       GROUP_CONCAT(DISTINCT dst_n.layer) AS callee_layers "
    "FROM edges e "
    "JOIN nodes src_n ON src_n.id = e.src_id "
    "JOIN nodes dst_n ON dst_n.id = e.dst_id "
    "WHERE e.relation_type IN ("
    "    'imports','calls','references','flows_to','controls_flow',"
    "    'writes_to','reads_from','invokes_provider','invokes_dynamic',"
    "    'routes_through','retrieves_via','resolves_callsite',"
    "    'emits_side_effect','applies','instantiates') "
    "  AND src_n.entity_type = 'module' "
    "  AND dst_n.layer IS NOT NULL AND dst_n.layer != '' "
    "GROUP BY src_n.resolved_path "
    "HAVING COUNT(DISTINCT dst_n.layer) >= 3 "
    "ORDER BY COUNT(DISTINCT dst_n.layer) DESC, COUNT(DISTINCT e.dst_id) DESC "
    "LIMIT 20"
).fetchall():
    print(r)

con.close()
