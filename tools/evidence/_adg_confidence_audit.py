# ruff: noqa: UP031, E702
"""ADG confidence routing audit -- targeted queries, read-only."""

import sqlite3

DB = r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03132026_0840.sqlite"
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
cur = db.cursor()

# --- Meta ---
cur.execute("SELECT key, value FROM meta")
print("=== META ===")
for r in cur.fetchall():
    print("  %s = %s" % (r[0], str(r[1])[:80]))

# --- Total counts ---
cur.execute("SELECT COUNT(*) FROM nodes")
print("\nTOTAL NODES:", cur.fetchone()[0])
cur.execute("SELECT COUNT(*) FROM edges")
print("TOTAL EDGES:", cur.fetchone()[0])

# --- Q1: All MODULE nodes for the 5 target files ---
print("\n=== Q1: TARGET FILE NODES ===")
TARGET_FRAGMENTS = [
    "healing_tier_config",
    "_ssot_types",
    "_ssot_routing",
    "_ssot_reporting",
    "heal_policy_types",
    "tiered_batch_util",
    "healing_tier_router",
    "qwen_meta_learning",
]
for frag in TARGET_FRAGMENTS:
    cur.execute(
        "SELECT id, adg_name, entity_type, layer, resolved_path FROM nodes "
        "WHERE resolved_path LIKE ? AND entity_type='module' "
        "AND resolved_path NOT LIKE '%archive%' AND resolved_path NOT LIKE '%backup%' "
        "AND resolved_path NOT LIKE '%healing_backup%'",
        ("%" + frag + "%",),
    )
    for r in cur.fetchall():
        print("  [%s] id=%s layer=%s path=%s" % (r["entity_type"], r["id"], r["layer"], r["resolved_path"]))

# --- Q2: All symbols named HEALING_CONFIDENCE_* ---
print("\n=== Q2: HEALING_CONFIDENCE SYMBOL DEFINITIONS ===")
cur.execute(
    "SELECT id, adg_name, entity_type, layer, resolved_path FROM nodes "
    "WHERE adg_name LIKE '%HEALING_CONFIDENCE%' AND resolved_path NOT LIKE '%archive%'",
)
hc_nodes = {r["id"]: r for r in cur.fetchall()}
for nid, r in hc_nodes.items():
    print("  id=%s [%s] %s in %s" % (nid, r["entity_type"], r["adg_name"], r["resolved_path"]))

# --- Q3: Who imports HEALING_CONFIDENCE_X or Y (direct importers) ---
print("\n=== Q3: DIRECT IMPORTERS OF HEALING_CONFIDENCE_X/Y (production code only) ===")
if hc_nodes:
    placeholders = ",".join("?" * len(hc_nodes))
    cur.execute(
        "SELECT DISTINCT n_src.resolved_path, e.relation_type, e.symbol "
        "FROM edges e "
        "JOIN nodes n_src ON e.src_id = n_src.id "
        "WHERE e.dst_id IN (%s) "
        "AND e.relation_type = 'imports' "
        "AND n_src.resolved_path NOT LIKE '%%archive%%' "
        "AND n_src.resolved_path NOT LIKE '%%backup%%' "
        "AND n_src.resolved_path NOT LIKE '%%healing_backup%%' "
        "ORDER BY n_src.resolved_path" % placeholders,
        list(hc_nodes.keys()),
    )
    for r in cur.fetchall():
        print("  %s  [sym=%s]" % (r["resolved_path"], r["symbol"]))

# --- Q4: All modules that have edges to/from _ssot_routing ---
print("\n=== Q4: EDGES TO/FROM _ssot_routing ===")
cur.execute(
    "SELECT id FROM nodes WHERE resolved_path LIKE '%_ssot_routing%' AND entity_type='module' "
    "AND resolved_path NOT LIKE '%archive%' AND resolved_path NOT LIKE '%backup%'",
)
ssot_ids = [r[0] for r in cur.fetchall()]
if ssot_ids:
    ph = ",".join("?" * len(ssot_ids))
    cur.execute(
        "SELECT DISTINCT n_src.resolved_path, e.relation_type, n_dst.resolved_path "
        "FROM edges e "
        "JOIN nodes n_src ON e.src_id=n_src.id "
        "JOIN nodes n_dst ON e.dst_id=n_dst.id "
        "WHERE (e.src_id IN (%s) OR e.dst_id IN (%s)) "
        "AND e.relation_type='imports' "
        "AND n_src.resolved_path NOT LIKE '%%archive%%' "
        "AND n_dst.resolved_path NOT LIKE '%%archive%%' "
        "ORDER BY e.relation_type, n_src.resolved_path" % (ph, ph),
        ssot_ids + ssot_ids,
    )
    for r in cur.fetchall():
        print("  %s -> %s  [%s]" % (r[0], r[2], r[1]))

# --- Q5: Layer violations involving routing files ---
print("\n=== Q5: GOVERNANCE LAYER VIOLATIONS (routing files) ===")
cur.execute(
    "SELECT e.relation_type, e.edge_kind, n_src.resolved_path, n_src.layer, n_dst.resolved_path, n_dst.layer "
    "FROM edges e "
    "JOIN nodes n_src ON e.src_id=n_src.id "
    "JOIN nodes n_dst ON e.dst_id=n_dst.id "
    "WHERE e.edge_kind='layer_violation' "
    "AND (n_src.resolved_path LIKE '%ssot%' OR n_src.resolved_path LIKE '%healing%' "
    "     OR n_dst.resolved_path LIKE '%ssot%' OR n_dst.resolved_path LIKE '%healing%') "
    "AND n_src.resolved_path NOT LIKE '%archive%' "
    "ORDER BY n_src.resolved_path LIMIT 40",
)
rows = cur.fetchall()
if not rows:
    print("  (none for routing files)")
for r in rows:
    print("  VIOLATION: %s (L%s) -> %s (L%s) [%s]" % (r[2], r[3], r[4], r[5], r[0]))

# --- Q6: ALL layer_violation edges (counts) ---
print("\n=== Q6: ALL LAYER VIOLATION EDGE COUNTS ===")
cur.execute("SELECT COUNT(*) FROM edges WHERE edge_kind='layer_violation'")
print("  Total layer_violation edges:", cur.fetchone()[0])
cur.execute(
    "SELECT n_src.layer, n_dst.layer, COUNT(*) cnt FROM edges e "
    "JOIN nodes n_src ON e.src_id=n_src.id "
    "JOIN nodes n_dst ON e.dst_id=n_dst.id "
    "WHERE e.edge_kind='layer_violation' "
    "GROUP BY n_src.layer, n_dst.layer ORDER BY cnt DESC LIMIT 20",
)
for r in cur.fetchall():
    print("  L%s -> L%s: %d violations" % (r[0], r[1], r[2]))

# --- Q7: All modules that contain 'ConfidenceScore' symbol references ---
print("\n=== Q7: NODES NAMED ConfidenceScore ===")
cur.execute(
    "SELECT id, adg_name, entity_type, layer, resolved_path FROM nodes "
    "WHERE adg_name LIKE '%ConfidenceScore%' "
    "AND resolved_path NOT LIKE '%archive%' AND resolved_path NOT LIKE '%backup%'",
)
cs_nodes = {r["id"]: r for r in cur.fetchall()}
for nid, r in cs_nodes.items():
    print("  [%s] %s  path=%s" % (r["entity_type"], r["adg_name"], r["resolved_path"]))

# --- Q8: Who uses ConfidenceScore ---
print("\n=== Q8: IMPORTERS OF ConfidenceScore ===")
if cs_nodes:
    ph = ",".join("?" * len(cs_nodes))
    cur.execute(
        "SELECT DISTINCT n_src.resolved_path "
        "FROM edges e JOIN nodes n_src ON e.src_id=n_src.id "
        "WHERE e.dst_id IN (%s) AND e.relation_type='imports' "
        "AND n_src.resolved_path NOT LIKE '%%archive%%' "
        "AND n_src.resolved_path NOT LIKE '%%backup%%' "
        "ORDER BY n_src.resolved_path" % ph,
        list(cs_nodes.keys()),
    )
    for r in cur.fetchall():
        print("  %s" % r[0])

# --- Q9: Nodes named SovereignDecisionEngine or calculate_healing_confidence ---
print("\n=== Q9: SovereignDecisionEngine / calculate_healing_confidence NODES ===")
cur.execute(
    "SELECT id, adg_name, entity_type, layer, resolved_path FROM nodes "
    "WHERE (adg_name LIKE '%SovereignDecisionEngine%' OR adg_name LIKE '%calculate_healing_confidence%') "
    "AND resolved_path NOT LIKE '%archive%' AND resolved_path NOT LIKE '%backup%'",
)
for r in cur.fetchall():
    print("  [%s] %s  path=%s" % (r["entity_type"], r["adg_name"], r["resolved_path"]))

# --- Q10: Snapshot ---
print("\n=== Q10: ADG SNAPSHOT METRICS ===")
import json
import os

snap = r"C:\Git\Agentic-Workflow\artifacts\adg\adg_snapshot_03132026_0840.json"
# guardian: allow-path-string
if os.path.exists(snap):
    with open(snap) as f:
        data = json.load(f)
    for k, v in data.items():
        print("  %s: %s" % (k, str(v)[:120]))

db.close()
print("\nDONE.")
