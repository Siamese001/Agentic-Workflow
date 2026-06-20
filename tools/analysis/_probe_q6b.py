# W6 ADG consumer mode declaration (per .codex/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"

# Probe: how module nodes relate to symbol nodes for edge joins.
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DB = str(REPO_ROOT / "artifacts" / "adg" / "adg_indexed_04252026_0521.sqlite")
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = con.cursor()

# Module node for path_constants
print("=== Module node for path_constants.py ===")
for r in cur.execute(
    "SELECT id, adg_name, entity_type, resolved_path, layer "
    "FROM nodes WHERE resolved_path = 'agentic_core/L0_routing/config/path_constants.py' "
    "LIMIT 10"
).fetchall():
    print(r)

print("\n=== Symbol nodes in path_constants.py ===")
for r in cur.execute(
    "SELECT id, adg_name, entity_type, resolved_path, layer "
    "FROM nodes WHERE resolved_path = 'agentic_core/L0_routing/config/path_constants.py' "
    "AND entity_type = 'symbol' LIMIT 10"
).fetchall():
    print(r)

print("\n=== Edges targeting path_constants symbols (sample) ===")
for r in cur.execute(
    "SELECT e.id, e.src_id, e.dst_id, e.relation_type, src_n.adg_name, src_n.layer, "
    "       dst_n.adg_name, dst_n.entity_type "
    "FROM edges e "
    "JOIN nodes dst_n ON dst_n.id = e.dst_id "
    "JOIN nodes src_n ON src_n.id = e.src_id "
    "WHERE dst_n.resolved_path = 'agentic_core/L0_routing/config/path_constants.py' "
    "AND dst_n.entity_type = 'symbol' "
    "LIMIT 10"
).fetchall():
    print(r)

print("\n=== Can we join centrality module to edges via resolved_path? ===")
for r in cur.execute(
    "SELECT h.node_id, h.adg_name, h.fan_in, h.layer, "
    "       COUNT(DISTINCT src_n.layer) as caller_layer_count, "
    "       GROUP_CONCAT(DISTINCT src_n.layer) as caller_layers "
    "FROM mv_hotspot_centrality h "
    "JOIN nodes sym ON sym.resolved_path = h.resolved_path AND sym.entity_type = 'symbol' "
    "JOIN edges e ON e.dst_id = sym.id "
    "JOIN nodes src_n ON src_n.id = e.src_id "
    "WHERE h.fan_in >= 5 "
    "AND e.relation_type IN ('imports','calls','references','flows_to') "
    "GROUP BY h.node_id "
    "HAVING COUNT(DISTINCT src_n.layer) >= 3 "
    "ORDER BY h.fan_in DESC LIMIT 10"
).fetchall():
    print(r)

con.close()
