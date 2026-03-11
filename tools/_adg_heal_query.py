"""Query refreshed ADG for healing/routing dependency subgraph."""

import glob
import sqlite3

files = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))
db = files[-1]
print("DB:", db)

conn = sqlite3.connect(db)
cur = conn.cursor()

HEAL_TERMS = [
    "%healing_tier_router%",
    "%healing_tier_dispatcher%",
    "%healing_tier_config%",
    "%healing_tier_types%",
    "%healing_provider_adapters%",
    "%healing_event_emitter%",
    "%qwen_vllm_inference%",
    "%qwen_circuit_breaker%",
    "%qwen_gpu_validator%",
    "%qwen_health%",
    "%qwen_determinism%",
    "%qwen_meta_learning%",
    "%tiering_allowlist%",
    "%remediation_dispatcher%",
    "%execute_ssot%",
    "%vllm_routing_predicates%",
]

# Build WHERE clause
where = " OR ".join(["n.adg_name LIKE ?" for _ in HEAL_TERMS])
cur.execute(
    f"SELECT n.id, n.adg_name, n.entity_type, n.layer, n.confidence, n.resolved_path "
    f"FROM nodes n WHERE {where} ORDER BY n.layer, n.adg_name",
    HEAL_TERMS,
)
nodes = cur.fetchall()
print(f"\n=== HEALING/ROUTING NODES ({len(nodes)}) ===")
node_ids = set()
for r in nodes:
    node_ids.add(r[0])
    try:
        conf_str = f"{float(r[4]):.2f}"
    except (TypeError, ValueError):
        conf_str = str(r[4])
    print(f"  [{r[3]}] {r[1]}  type={r[2]}  conf={conf_str}  path={r[5]}")

# Get all direct import edges BETWEEN these nodes
if node_ids:
    placeholders = ",".join("?" * len(node_ids))
    cur.execute(
        f"SELECT n_src.adg_name, e.relation_type, n_dst.adg_name, e.edge_kind "
        f"FROM edges e "
        f"JOIN nodes n_src ON e.src_id = n_src.id "
        f"JOIN nodes n_dst ON e.dst_id = n_dst.id "
        f"WHERE e.src_id IN ({placeholders}) AND e.dst_id IN ({placeholders}) "
        f"ORDER BY n_src.adg_name, e.relation_type",
        list(node_ids) + list(node_ids),
    )
    edges = cur.fetchall()
    print(f"\n=== INTRA-SUBGRAPH EDGES ({len(edges)}) ===")
    for e in edges:
        print(f"  {e[0]}  --[{e[1]}/{e[2]}]-->  {e[2]}")

# Who imports healing_tier_dispatcher (callers)
cur.execute(
    "SELECT n_src.adg_name, e.relation_type, n_dst.adg_name "
    "FROM edges e "
    "JOIN nodes n_src ON e.src_id = n_src.id "
    "JOIN nodes n_dst ON e.dst_id = n_dst.id "
    "WHERE n_dst.adg_name LIKE '%healing_tier_dispatcher%' "
    "   OR n_dst.adg_name LIKE '%healing_tier_router%' "
    "ORDER BY n_src.adg_name",
)
callers = cur.fetchall()
print(f"\n=== CALLERS OF DISPATCHER/ROUTER ({len(callers)}) ===")
for c in callers:
    print(f"  {c[0]}  --[{c[1]}]-->  {c[2]}")

# Who imports execute_ssot
cur.execute(
    "SELECT n_src.adg_name, e.relation_type, n_dst.adg_name "
    "FROM edges e "
    "JOIN nodes n_src ON e.src_id = n_src.id "
    "JOIN nodes n_dst ON e.dst_id = n_dst.id "
    "WHERE n_dst.adg_name LIKE '%execute_ssot%' "
    "ORDER BY n_src.adg_name",
)
ssot_callers = cur.fetchall()
print(f"\n=== CALLERS OF execute_ssot ({len(ssot_callers)}) ===")
for c in ssot_callers:
    print(f"  {c[0]}  --[{c[1]}]-->  {c[2]}")

# Violations touching healing routing nodes
if node_ids:
    placeholders = ",".join("?" * len(node_ids))
    cur.execute(
        f"SELECT n_src.adg_name, e.relation_type, e.edge_kind, n_dst.adg_name "
        f"FROM edges e "
        f"JOIN nodes n_src ON e.src_id = n_src.id "
        f"JOIN nodes n_dst ON e.dst_id = n_dst.id "
        f"WHERE (e.src_id IN ({placeholders}) OR e.dst_id IN ({placeholders})) "
        f"  AND e.edge_kind = 'GV_violates' "
        f"ORDER BY n_src.adg_name",
        list(node_ids) + list(node_ids),
    )
    violations = cur.fetchall()
    print(f"\n=== VIOLATIONS IN HEALING SUBGRAPH ({len(violations)}) ===")
    for v in violations:
        print(f"  {v[0]}  --[{v[1]}/{v[2]}]-->  {v[3]}")

conn.close()
