# ruff: noqa: UP031
"""ADG confidence routing audit -- phase 3 (fixed)."""

import sqlite3

DB = r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03132026_0840.sqlite"
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
cur = db.cursor()

TARGET = [
    "_ssot_types",
    "_ssot_routing",
    "_ssot_reporting",
    "heal_policy_types",
    "tiered_batch_util",
    "healing_tier_router",
    "healing_tier_config",
    "qwen_meta_learning",
]

# --- Q23: dead imports in target files ---
print("=== Q23: DEAD IMPORTS IN TARGET FILES ===")
cur.execute(
    "SELECT e.symbol, n_src.resolved_path FROM edges e "
    "JOIN nodes n_src ON e.src_id=n_src.id "
    "WHERE e.edge_kind='dead_imports' "
    "AND n_src.resolved_path NOT LIKE '%archive%' AND n_src.resolved_path NOT LIKE '%backup%'",
)
dead = [r for r in cur.fetchall() if any(p in (r["resolved_path"] or "") for p in TARGET)]
print("  count:", len(dead))
for r in dead:
    print("    sym=%-50s  file=%s" % (str(r["symbol"])[:50], r["resolved_path"]))

# --- Q24: antipatterns in target files ---
print("\n=== Q24: ANTIPATTERN EDGES IN TARGET FILES ===")
cur.execute(
    "SELECT e.symbol, e.edge_kind, n_src.resolved_path, n_dst.adg_name "
    "FROM edges e "
    "JOIN nodes n_src ON e.src_id=n_src.id "
    "JOIN nodes n_dst ON e.dst_id=n_dst.id "
    "WHERE e.edge_kind='antipattern' "
    "AND n_src.resolved_path NOT LIKE '%archive%' AND n_src.resolved_path NOT LIKE '%backup%'",
)
aps = [r for r in cur.fetchall() if any(p in (r["resolved_path"] or "") for p in TARGET)]
print("  count:", len(aps))
for r in aps:
    print(
        "    [%s] sym=%-40s  dst=%s  file=%s"
        % (r["edge_kind"], str(r["symbol"])[:40], r["n_dst.adg_name"], r["resolved_path"]),
    )

# --- Q25: reads_env in target files ---
print("\n=== Q25: reads_env IN TARGET FILES ===")
cur.execute(
    "SELECT e.symbol, e.relation_type, n_src.resolved_path FROM edges e "
    "JOIN nodes n_src ON e.src_id=n_src.id "
    "WHERE e.relation_type='reads_env' "
    "AND n_src.resolved_path NOT LIKE '%archive%' AND n_src.resolved_path NOT LIKE '%backup%'",
)
envs = [r for r in cur.fetchall() if any(p in (r["resolved_path"] or "") for p in TARGET)]
print("  count:", len(envs))
for r in envs:
    print("    sym=%-50s  file=%s" % (str(r["symbol"])[:50], r["resolved_path"]))

# --- Q26: all edge kinds and relation types ---
print("\n=== Q26: ALL EDGE_KINDS ===")
cur.execute("SELECT DISTINCT edge_kind FROM edges WHERE edge_kind IS NOT NULL ORDER BY edge_kind")
print("  " + str([r[0] for r in cur.fetchall()]))

# --- Q27: execute_ssot.py class/function symbols ---
print("\n=== Q27: execute_ssot.py SYMBOL DEFS ===")
cur.execute(
    "SELECT adg_name, entity_type FROM nodes "
    "WHERE resolved_path LIKE '%execute_ssot.py' "
    "AND entity_type IN ('class','function','constant') "
    "AND resolved_path NOT LIKE '%archive%' AND resolved_path NOT LIKE '%test%' "
    "LIMIT 40",
)
for r in cur.fetchall():
    print("  [%s] %s" % (r["entity_type"], r["adg_name"]))

# --- Q28: _ssot_reporting.py module node + imports ---
print("\n=== Q28: _ssot_reporting.py MODULE + IMPORTS ===")
cur.execute(
    "SELECT id, adg_name, entity_type, layer, resolved_path FROM nodes "
    "WHERE resolved_path LIKE '%_ssot_reporting%' AND entity_type='module' "
    "AND resolved_path NOT LIKE '%archive%' AND resolved_path NOT LIKE '%backup%'",
)
rep_nodes = {r["id"]: dict(r) for r in cur.fetchall()}
for nid, r in rep_nodes.items():
    print("  MODULE: %s" % r["resolved_path"])
    cur.execute(
        "SELECT e.relation_type, e.symbol, n_dst.resolved_path "
        "FROM edges e JOIN nodes n_dst ON e.dst_id=n_dst.id "
        "WHERE e.src_id=? AND e.relation_type='imports' ORDER BY n_dst.resolved_path",
        (nid,),
    )
    for e in cur.fetchall():
        print("    imports: sym=%-60s  path=%s" % (str(e["symbol"])[:60], e["resolved_path"]))

# --- Q29: importers of _ssot_reporting ---
print("\n=== Q29: IMPORTERS OF _ssot_reporting ===")
if rep_nodes:
    ph = ",".join("?" * len(rep_nodes))
    cur.execute(
        "SELECT DISTINCT n_src.resolved_path FROM edges e "
        "JOIN nodes n_src ON e.src_id=n_src.id "
        "WHERE e.dst_id IN (%s) AND e.relation_type='imports' "
        "AND n_src.resolved_path NOT LIKE '%%archive%%' "
        "ORDER BY n_src.resolved_path" % ph,
        list(rep_nodes.keys()),
    )
    for r in cur.fetchall():
        print("  %s" % r[0])

# --- Q30: Any node that references SOVEREIGN_HIGH_CONFIDENCE or SOVEREIGN_MEDIUM_CONFIDENCE ---
print("\n=== Q30: SOVEREIGN_*_CONFIDENCE env var references ===")
cur.execute(
    "SELECT e.symbol, n_src.resolved_path FROM edges e "
    "JOIN nodes n_src ON e.src_id=n_src.id "
    "WHERE e.symbol LIKE '%SOVEREIGN%CONFIDENCE%' "
    "AND n_src.resolved_path NOT LIKE '%archive%'",
)
sov = cur.fetchall()
print("  count:", len(sov))
for r in sov:
    print("    sym=%s  file=%s" % (r["symbol"], r["resolved_path"]))

db.close()
print("\nDONE.")
