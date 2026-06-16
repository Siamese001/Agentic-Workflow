# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"

# Quick probe: check edge dst_id vs centrality node_id alignment.
import sqlite3
from pathlib import Path, json

REPO_ROOT = Path(__file__).resolve().parents[2]
DB = str(REPO_ROOT / "artifacts" / "adg" / "adg_indexed_04252026_0521.sqlite")
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = con.cursor()

# Edge dst_id types
print("=== Edge dst_id entity_type distribution (top 10) ===")
for r in cur.execute(
    "SELECT n.entity_type, COUNT(*) as cnt "
    "FROM edges e JOIN nodes n ON n.id = e.dst_id "
    "WHERE e.relation_type = 'imports' "
    "GROUP BY n.entity_type ORDER BY cnt DESC LIMIT 10"
).fetchall():
    print(r)

print("\n=== Centrality node_id entity_type distribution (top 10) ===")
for r in cur.execute(
    "SELECT n.entity_type, COUNT(*) as cnt "
    "FROM mv_hotspot_centrality h JOIN nodes n ON n.id = h.node_id "
    "GROUP BY n.entity_type ORDER BY cnt DESC LIMIT 10"
).fetchall():
    print(r)

print("\n=== Overlap: how many centrality node_ids appear as edge dst_id? ===")
overlap = cur.execute(
    "SELECT COUNT(DISTINCT h.node_id) "
    "FROM mv_hotspot_centrality h "
    "WHERE EXISTS (SELECT 1 FROM edges e WHERE e.dst_id = h.node_id) "
    "AND h.fan_in >= 5"
).fetchone()[0]
total = cur.execute("SELECT COUNT(*) FROM mv_hotspot_centrality WHERE fan_in >= 5").fetchone()[0]
print(f"  {overlap} of {total} high-fanin nodes appear as edge dst_id")

print("\n=== Sample: top 5 centrality nodes with imports edges ===")
for r in cur.execute(
    "SELECT h.node_id, h.adg_name, h.fan_in, h.layer, "
    "       COUNT(DISTINCT src_n.layer) as caller_layers, "
    "       GROUP_CONCAT(DISTINCT src_n.layer) as layers "
    "FROM mv_hotspot_centrality h "
    "JOIN edges e ON e.dst_id = h.node_id "
    "JOIN nodes src_n ON src_n.id = e.src_id "
    "WHERE h.fan_in >= 5 AND e.relation_type IN ('imports','calls','references','flows_to') "
    "GROUP BY h.node_id "
    "HAVING COUNT(DISTINCT src_n.layer) >= 3 "
    "ORDER BY h.fan_in DESC LIMIT 5"
).fetchall():
    print(r)

con.close()
