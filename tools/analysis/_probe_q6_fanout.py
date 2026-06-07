# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"

# Probe: check fan-out side of resolved_path join
import sqlite3

DB = r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_04252026_0521.sqlite"
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = con.cursor()

# Check: do symbol nodes appear as src_id in edges?
print("=== Edge src_id entity_type distribution ===")
for r in cur.execute(
    "SELECT n.entity_type, COUNT(*) as cnt "
    "FROM edges e JOIN nodes n ON n.id = e.src_id "
    "GROUP BY n.entity_type ORDER BY cnt DESC LIMIT 10"
).fetchall():
    print(r)

# Test the join directly
print("\n=== Q6 test: top 5 fan-out modules with >=3 callee layers ===")
for r in cur.execute(
    "SELECT h.node_id, h.adg_name, h.layer AS caller_layer, "
    "       h.resolved_path, h.fan_out, "
    "       COUNT(DISTINCT dst_n.layer) AS callee_layer_count, "
    "       GROUP_CONCAT(DISTINCT dst_n.layer) AS callee_layers "
    "FROM mv_hotspot_centrality h "
    "JOIN nodes sym ON sym.resolved_path = h.resolved_path AND sym.entity_type = 'symbol' "
    "JOIN edges e ON e.src_id = sym.id "
    "JOIN nodes dst_n ON dst_n.id = e.dst_id "
    "WHERE h.fan_out >= 5 "
    "  AND e.relation_type IN ('imports','calls','references','flows_to','controls_flow') "
    "GROUP BY h.node_id "
    "HAVING COUNT(DISTINCT dst_n.layer) >= 3 "
    "ORDER BY h.fan_out DESC LIMIT 10"
).fetchall():
    print(r)

con.close()
