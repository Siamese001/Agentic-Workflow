# ruff: noqa: UP031
"""ADG confidence routing audit -- phase 2, anti-patterns + blast radius."""

import json
import sqlite3

DB = r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03132026_0840.sqlite"
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
cur = db.cursor()

# --- Q11: antipattern edges involving routing/confidence files ---
print("=== Q11: ANTIPATTERN EDGES (routing/confidence scope) ===")
cur.execute(
    "SELECT e.symbol, e.edge_kind, e.source_file, n_src.resolved_path, n_dst.resolved_path "
    "FROM edges e "
    "JOIN nodes n_src ON e.src_id=n_src.id "
    "JOIN nodes n_dst ON e.dst_id=n_dst.id "
    "WHERE e.edge_kind='antipattern' "
    "AND (n_src.resolved_path LIKE '%ssot%' OR n_src.resolved_path LIKE '%healing%' "
    "  OR n_src.resolved_path LIKE '%heal_policy%' OR n_src.resolved_path LIKE '%tiered_batch%') "
    "AND n_src.resolved_path NOT LIKE '%archive%' "
    "AND n_src.resolved_path NOT LIKE '%backup%' "
    "LIMIT 80",
)
rows = cur.fetchall()
if not rows:
    print("  (none directly matching routing files)")
for r in rows:
    print(
        "  [%s] sym=%s  src=%s -> dst=%s  file=%s"
        % (r["edge_kind"], r["symbol"], r["resolved_path"], r[4], r["source_file"]),
    )

# --- Q12: All antipattern edges by symbol (top patterns) ---
print("\n=== Q12: TOP ANTIPATTERN SYMBOLS ===")
cur.execute(
    "SELECT e.symbol, COUNT(*) cnt FROM edges e WHERE e.edge_kind='antipattern' "
    "GROUP BY e.symbol ORDER BY cnt DESC LIMIT 30",
)
for r in cur.fetchall():
    print("  %-50s: %d" % (str(r[0])[:50], r[1]))

# --- Q13: qwen_meta_learning - does it re-declare HEALING_CONFIDENCE? ---
print("\n=== Q13: qwen_meta_learning NODES ===")
cur.execute(
    "SELECT id, adg_name, entity_type, layer, resolved_path FROM nodes "
    "WHERE resolved_path LIKE '%qwen_meta_learning%' "
    "AND resolved_path NOT LIKE '%archive%' AND resolved_path NOT LIKE '%backup%'",
)
qml_nodes = {r["id"]: dict(r) for r in cur.fetchall()}
for nid, r in qml_nodes.items():
    print("  [%s] %s  path=%s" % (r["entity_type"], r["adg_name"], r["resolved_path"]))

# --- Q14: execute_ssot.py has duplicate SovereignDecisionEngine? ---
print("\n=== Q14: execute_ssot.py imports + symbols ===")
cur.execute(
    "SELECT id, adg_name, entity_type, resolved_path FROM nodes "
    "WHERE resolved_path LIKE '%execute_ssot%' AND entity_type='module' "
    "AND resolved_path NOT LIKE '%archive%' AND resolved_path NOT LIKE '%backup%' "
    "AND resolved_path NOT LIKE '%test%'",
)
exssot_nodes = {r["id"]: dict(r) for r in cur.fetchall()}
for nid, r in exssot_nodes.items():
    print("  MODULE: %s" % r["resolved_path"])
    cur.execute(
        "SELECT e.relation_type, e.symbol, n_dst.resolved_path "
        "FROM edges e JOIN nodes n_dst ON e.dst_id=n_dst.id "
        "WHERE e.src_id=? AND e.relation_type='imports' "
        "AND n_dst.resolved_path NOT LIKE '%archive%' "
        "ORDER BY n_dst.resolved_path",
        (nid,),
    )
    for e in cur.fetchall():
        print("    imports: %s  [sym=%s]" % (e["resolved_path"], e["symbol"]))

# --- Q15: All modules importing from _ssot_types (to find ConfidenceScore consumers) ---
print("\n=== Q15: IMPORTERS OF _ssot_types ===")
cur.execute(
    "SELECT id FROM nodes WHERE resolved_path LIKE '%_ssot_types%' AND entity_type='module' "
    "AND resolved_path NOT LIKE '%archive%'",
)
ssot_type_ids = [r[0] for r in cur.fetchall()]
if ssot_type_ids:
    ph = ",".join("?" * len(ssot_type_ids))
    cur.execute(
        "SELECT DISTINCT n_src.resolved_path FROM edges e "
        "JOIN nodes n_src ON e.src_id=n_src.id "
        "WHERE e.dst_id IN (%s) AND e.relation_type='imports' "
        "AND n_src.resolved_path NOT LIKE '%%archive%%' "
        "AND n_src.resolved_path NOT LIKE '%%backup%%' "
        "ORDER BY n_src.resolved_path" % ph,
        ssot_type_ids,
    )
    for r in cur.fetchall():
        print("  %s" % r[0])

# --- Q16: All modules importing from heal_policy_types ---
print("\n=== Q16: IMPORTERS OF heal_policy_types ===")
cur.execute(
    "SELECT id FROM nodes WHERE resolved_path LIKE '%heal_policy_types%' AND entity_type='module' "
    "AND resolved_path NOT LIKE '%archive%'",
)
hpt_ids = [r[0] for r in cur.fetchall()]
if hpt_ids:
    ph = ",".join("?" * len(hpt_ids))
    cur.execute(
        "SELECT DISTINCT n_src.resolved_path FROM edges e "
        "JOIN nodes n_src ON e.src_id=n_src.id "
        "WHERE e.dst_id IN (%s) AND e.relation_type='imports' "
        "AND n_src.resolved_path NOT LIKE '%%archive%%' "
        "AND n_src.resolved_path NOT LIKE '%%backup%%' "
        "ORDER BY n_src.resolved_path" % ph,
        hpt_ids,
    )
    for r in cur.fetchall():
        print("  %s" % r[0])

# --- Q17: All modules importing tiered_batch_util ---
print("\n=== Q17: IMPORTERS OF tiered_batch_util ===")
cur.execute(
    "SELECT id FROM nodes WHERE resolved_path LIKE '%tiered_batch_util%' AND entity_type='module' "
    "AND resolved_path NOT LIKE '%archive%'",
)
tbu_ids = [r[0] for r in cur.fetchall()]
if tbu_ids:
    ph = ",".join("?" * len(tbu_ids))
    cur.execute(
        "SELECT DISTINCT n_src.resolved_path FROM edges e "
        "JOIN nodes n_src ON e.src_id=n_src.id "
        "WHERE e.dst_id IN (%s) AND e.relation_type='imports' "
        "AND n_src.resolved_path NOT LIKE '%%archive%%' "
        "AND n_src.resolved_path NOT LIKE '%%backup%%' "
        "ORDER BY n_src.resolved_path" % ph,
        tbu_ids,
    )
    for r in cur.fetchall():
        print("  %s" % r[0])
else:
    print("  (no importers found or no module node)")

# --- Q18: accesses_credential edge count + sample (for hardcoded secrets check) ---
print("\n=== Q18: accesses_credential EDGES (sample 10) ===")
cur.execute(
    "SELECT e.symbol, n_src.resolved_path FROM edges e "
    "JOIN nodes n_src ON e.src_id=n_src.id "
    "WHERE e.edge_kind='accesses_credential' "
    "AND n_src.resolved_path NOT LIKE '%archive%' AND n_src.resolved_path NOT LIKE '%backup%' "
    "ORDER BY n_src.resolved_path LIMIT 10",
)
for r in cur.fetchall():
    print("  sym=%s  file=%s" % (r["symbol"], r["resolved_path"]))
cur.execute("SELECT COUNT(*) FROM edges WHERE edge_kind='accesses_credential'")
print("  TOTAL accesses_credential:", cur.fetchone()[0])

# --- Q19: graph_plane_counts from snapshot ---
print("\n=== Q19: SNAPSHOT GRAPH PLANE COUNTS ===")
snap = r"C:\Git\Agentic-Workflow\artifacts\adg\adg_snapshot_03132026_0840.json"
import os

# guardian: allow-path-string
if os.path.exists(snap):
    with open(snap) as f:
        data = json.load(f)
    gpc = data.get("graph_plane_counts", {})
    for k, v in sorted(gpc.items()):
        print("  %s: %s" % (k, v))
    print("\n  BLIND SPOTS:", data.get("blind_spots", {}))
    print("  COUNTS:", data.get("counts", {}))
    bylayer = data.get("by_layer", {})
    print("  BY LAYER:", bylayer)

# --- Q20: All HEALING_CONFIDENCE_X symbol definitions (check for re-declarations) ---
print("\n=== Q20: ALL HEALING_CONFIDENCE_X DEFINITIONS ===")
cur.execute(
    "SELECT adg_name, entity_type, resolved_path FROM nodes "
    "WHERE adg_name LIKE '%HEALING_CONFIDENCE_X%' "
    "AND entity_type != 'module' "
    "AND resolved_path NOT LIKE '%archive%' AND resolved_path NOT LIKE '%backup%'",
)
for r in cur.fetchall():
    print("  [%s] %s  path=%s" % (r["entity_type"], r["adg_name"], r["resolved_path"]))

db.close()
print("\nDONE.")
