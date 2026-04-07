# ruff: noqa: UP031
"""ADG blast radius for routing consolidation -- read-only."""

import sqlite3

DB = r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03132026_0840.sqlite"
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
cur = db.cursor()

TARGETS = [
    "decide_heal_escalation",
    "classify_score",
    "classify_confidence",
    "decide_reasoning_tier",
    "should_proceed_with_healing",
    "route_healing_tier",
    "compute_heal_confidence",
    "HealEscalationInputs",
    "HealEscalationDecision",
    "TieredBatchProcessor",
]

for sym in TARGETS:
    cur.execute(
        "SELECT id, adg_name, entity_type, resolved_path FROM nodes "
        "WHERE adg_name LIKE ? AND resolved_path NOT LIKE '%archive%' AND resolved_path NOT LIKE '%backup%'",
        ("%" + sym + "%",),
    )
    nodes = {r["id"]: dict(r) for r in cur.fetchall()}
    callers = []
    if nodes:
        ph = ",".join("?" * len(nodes))
        cur.execute(
            "SELECT DISTINCT n_src.resolved_path, e.relation_type FROM edges e "
            "JOIN nodes n_src ON e.src_id=n_src.id "
            "WHERE e.dst_id IN (%s) AND e.relation_type IN ('imports','calls') "
            "AND n_src.resolved_path NOT LIKE '%%archive%%' AND n_src.resolved_path NOT LIKE '%%backup%%' "
            "ORDER BY n_src.resolved_path" % ph,
            list(nodes.keys()),
        )
        callers = cur.fetchall()
    print("=== %s ===" % sym)
    for nid, n in nodes.items():
        print("  DEF [%s] %s" % (n["entity_type"], n["resolved_path"]))
    for c in callers:
        print("  CALLER [%s] %s" % (c["relation_type"], c["resolved_path"]))
    print()

# Also find all callers of ConfidenceScore routing properties
print("=== ConfidenceScore.is_high_confidence / is_medium_confidence / is_low_confidence ===")
for prop in ["is_high_confidence", "is_medium_confidence", "is_low_confidence"]:
    cur.execute(
        "SELECT id FROM nodes WHERE adg_name LIKE ? AND resolved_path NOT LIKE '%archive%'",
        ("%" + prop + "%",),
    )
    pnodes = {r[0] for r in cur.fetchall()}
    if pnodes:
        ph = ",".join("?" * len(pnodes))
        cur.execute(
            "SELECT DISTINCT n_src.resolved_path FROM edges e "
            "JOIN nodes n_src ON e.src_id=n_src.id "
            "WHERE e.dst_id IN (%s) AND n_src.resolved_path NOT LIKE '%%archive%%'" % ph,
            list(pnodes),
        )
        callers2 = cur.fetchall()
        if callers2:
            print("  %s callers:" % prop)
            for c in callers2:
                print("    %s" % c[0])

# Find all heal_policy_types importers with detail
print("\n=== heal_policy_types IMPORTERS (detailed) ===")
cur.execute(
    "SELECT id FROM nodes WHERE resolved_path LIKE '%heal_policy_types%' AND entity_type='module' "
    "AND resolved_path NOT LIKE '%archive%'",
)
hpt_ids = [r[0] for r in cur.fetchall()]
if hpt_ids:
    ph = ",".join("?" * len(hpt_ids))
    cur.execute(
        "SELECT DISTINCT n_src.resolved_path, e.symbol FROM edges e "
        "JOIN nodes n_src ON e.src_id=n_src.id "
        "WHERE e.dst_id IN (%s) AND e.relation_type='imports' "
        "AND n_src.resolved_path NOT LIKE '%%archive%%' "
        "ORDER BY n_src.resolved_path" % ph,
        hpt_ids,
    )
    for r in cur.fetchall():
        print("  %s  [sym=%s]" % (r[0], r[1]))
else:
    # Try via symbol nodes
    cur.execute(
        "SELECT id FROM nodes WHERE adg_name LIKE '%heal_policy_types%' "
        "AND resolved_path NOT LIKE '%archive%'",
    )
    sym_ids = [r[0] for r in cur.fetchall()]
    if sym_ids:
        ph = ",".join("?" * len(sym_ids))
        cur.execute(
            "SELECT DISTINCT n_src.resolved_path, e.symbol FROM edges e "
            "JOIN nodes n_src ON e.src_id=n_src.id "
            "WHERE e.dst_id IN (%s) "
            "AND n_src.resolved_path NOT LIKE '%%archive%%' "
            "ORDER BY n_src.resolved_path" % ph,
            sym_ids,
        )
        for r in cur.fetchall():
            print("  %s  [sym=%s]" % (r[0], r[1]))

# tiered_batch_util importers
print("\n=== tiered_batch_util IMPORTERS (via symbol) ===")
cur.execute(
    "SELECT id FROM nodes WHERE adg_name LIKE '%tiered_batch%' AND resolved_path NOT LIKE '%archive%'",
)
tbu_ids = [r[0] for r in cur.fetchall()]
if tbu_ids:
    ph = ",".join("?" * len(tbu_ids))
    cur.execute(
        "SELECT DISTINCT n_src.resolved_path, e.symbol FROM edges e "
        "JOIN nodes n_src ON e.src_id=n_src.id "
        "WHERE e.dst_id IN (%s) "
        "AND n_src.resolved_path NOT LIKE '%%archive%%' "
        "ORDER BY n_src.resolved_path" % ph,
        tbu_ids,
    )
    for r in cur.fetchall():
        print("  %s  [sym=%s]" % (r[0], r[1]))

db.close()
print("\nDONE.")
