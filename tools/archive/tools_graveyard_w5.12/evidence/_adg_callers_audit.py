# ruff: noqa: UP031
"""ADG caller audit -- find all consumers of the 5 routing systems."""

import sqlite3

DB = r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03132026_0840.sqlite"
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
cur = db.cursor()

SYMBOLS_OF_INTEREST = [
    "decide_heal_escalation",
    "classify_score",
    "classify_confidence",
    "decide_reasoning_tier",
    "should_proceed_with_healing",
    "calculate_healing_confidence",
    "route_healing_tier",
    "compute_heal_confidence",
    "is_high_confidence",
    "is_medium_confidence",
    "is_low_confidence",
    "heuristic_threshold",
    "SCORE_THRESHOLD_DET",
    "SCORE_THRESHOLD_QWEN",
    "HealEscalationInputs",
    "HealEscalationDecision",
    "ScoreBand",
    "ConfidenceLevel",
]

print("=== CALLERS OF ROUTING SYMBOLS ===")
for sym in SYMBOLS_OF_INTEREST:
    cur.execute(
        "SELECT DISTINCT n_src.resolved_path, e.relation_type "
        "FROM edges e "
        "JOIN nodes n_src ON e.src_id=n_src.id "
        "JOIN nodes n_dst ON e.dst_id=n_dst.id "
        "WHERE n_dst.adg_name LIKE ? "
        "AND e.relation_type IN ('imports','calls','uses','references') "
        "AND n_src.resolved_path NOT LIKE '%archive%' "
        "AND n_src.resolved_path NOT LIKE '%backup%' "
        "ORDER BY n_src.resolved_path",
        ("%" + sym + "%",),
    )
    callers = cur.fetchall()
    if callers:
        print("\n  %s (%d callers):" % (sym, len(callers)))
        for c in callers:
            print("    [%s] %s" % (c["relation_type"], c["resolved_path"]))

# Find all importers of heal_policy_types
print("\n=== IMPORTERS OF heal_policy_types (module) ===")
cur.execute(
    "SELECT id FROM nodes WHERE resolved_path LIKE '%heal_policy_types%' "
    "AND entity_type NOT LIKE '%symbol%' "
    "AND resolved_path NOT LIKE '%archive%'",
)
hpt_ids = [r[0] for r in cur.fetchall()]
print("  heal_policy_types module node ids:", hpt_ids)
if hpt_ids:
    ph = ",".join("?" * len(hpt_ids))
    cur.execute(
        "SELECT DISTINCT n_src.resolved_path, e.relation_type FROM edges e "
        "JOIN nodes n_src ON e.src_id=n_src.id "
        "WHERE e.dst_id IN (%s) "
        "AND n_src.resolved_path NOT LIKE '%%archive%%' "
        "ORDER BY n_src.resolved_path" % ph,
        hpt_ids,
    )
    for r in cur.fetchall():
        print("  [%s] %s" % (r["relation_type"], r["resolved_path"]))

# Find all importers of _ssot_routing via symbol edges
print("\n=== IMPORTERS OF _ssot_routing MODULE ===")
cur.execute(
    "SELECT id FROM nodes WHERE resolved_path LIKE '%_ssot_routing%' "
    "AND entity_type NOT LIKE '%symbol%' "
    "AND resolved_path NOT LIKE '%archive%'",
)
sr_ids = [r[0] for r in cur.fetchall()]
if sr_ids:
    ph = ",".join("?" * len(sr_ids))
    cur.execute(
        "SELECT DISTINCT n_src.resolved_path, e.relation_type FROM edges e "
        "JOIN nodes n_src ON e.src_id=n_src.id "
        "WHERE e.dst_id IN (%s) "
        "AND n_src.resolved_path NOT LIKE '%%archive%%' "
        "ORDER BY n_src.resolved_path" % ph,
        sr_ids,
    )
    print("  _ssot_routing importers:")
    for r in cur.fetchall():
        print("  [%s] %s" % (r["relation_type"], r["resolved_path"]))

# Count all edges TO/FROM each routing file
print("\n=== EDGE COUNTS BY TARGET FILE ===")
files = [
    "healing_tier_router",
    "heal_policy_types",
    "_ssot_routing",
    "_ssot_types",
    "tiered_batch_util",
]
for frag in files:
    cur.execute(
        "SELECT COUNT(*) FROM edges e "
        "JOIN nodes n ON e.dst_id=n.id "
        "WHERE n.resolved_path LIKE ? "
        "AND e.relation_type='imports' "
        "AND n.resolved_path NOT LIKE '%archive%'",
        ("%" + frag + "%",),
    )
    cnt = cur.fetchone()[0]
    print("  %s: %d import-edges pointing at it" % (frag, cnt))

db.close()
print("\nDONE.")
