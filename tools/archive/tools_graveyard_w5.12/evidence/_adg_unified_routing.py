# ruff: noqa: UP031
"""ADG-first unified routing consolidation analysis. Read-only SQLite queries only."""

import sqlite3

DB = r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03132026_0840.sqlite"
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
cur = db.cursor()

ROUTING_FRAGMENTS = [
    "healing_tier_router",
    "healing_tier_config",
    "heal_policy_types",
    "_ssot_routing",
    "_ssot_types",
    "_ssot_reporting",
    "tiered_batch_util",
    "qwen_meta_learning",
    "SovereignBaseAgent",
    "decorators_util",
    "healing_tier_dispatcher",
]

# ── Q1: Module nodes for all routing files ────────────────────────────────────
print("=== Q1: ROUTING MODULE NODES ===")
for frag in ROUTING_FRAGMENTS:
    cur.execute(
        "SELECT id, adg_name, entity_type, layer, resolved_path FROM nodes "
        "WHERE resolved_path LIKE ? AND entity_type='module' "
        "AND resolved_path NOT LIKE '%archive%' AND resolved_path NOT LIKE '%backup%'",
        ("%" + frag + "%",),
    )
    rows = cur.fetchall()
    for r in rows:
        print("  id=%-5d layer=%-8s %s" % (r["id"], str(r["layer"]), r["resolved_path"]))

# ── Q2: All ROUTING FUNCTION symbols ─────────────────────────────────────────
print("\n=== Q2: ROUTING FUNCTION SYMBOLS ===")
ROUTING_SYMS = [
    "route_healing_tier",
    "route_by_confidence",
    "compute_heal_confidence",
    "decide_heal_escalation",
    "classify_score",
    "classify_confidence",
    "decide_reasoning_tier",
    "compute_routing_decision",
    "should_proceed_with_healing",
    "_route_decision",
    "calculate_healing_confidence",
]
for sym in ROUTING_SYMS:
    cur.execute(
        "SELECT adg_name, entity_type, resolved_path FROM nodes "
        "WHERE adg_name LIKE ? AND resolved_path NOT LIKE '%archive%' "
        "AND resolved_path NOT LIKE '%test%'",
        ("%" + sym + "%",),
    )
    rows = cur.fetchall()
    if rows:
        print("  %s:" % sym)
        for r in rows:
            print("    [%s] %s  => %s" % (r["entity_type"], r["adg_name"], r["resolved_path"]))

# ── Q3: Who calls/imports each routing function (production only) ─────────────
print("\n=== Q3: PRODUCTION CALLERS OF EACH ROUTING FUNCTION ===")
for sym in ROUTING_SYMS:
    cur.execute(
        "SELECT DISTINCT n_src.resolved_path, e.relation_type, e.edge_kind "
        "FROM edges e "
        "JOIN nodes n_src ON e.src_id=n_src.id "
        "JOIN nodes n_dst ON e.dst_id=n_dst.id "
        "WHERE n_dst.adg_name LIKE ? "
        "AND e.relation_type IN ('imports','calls') "
        "AND n_src.resolved_path NOT LIKE '%archive%' "
        "AND n_src.resolved_path NOT LIKE '%backup%' "
        "AND n_src.resolved_path NOT LIKE '%test%' "
        "ORDER BY n_src.resolved_path",
        ("%" + sym + "%",),
    )
    rows = cur.fetchall()
    if rows:
        print("  %s (%d prod callers):" % (sym, len(rows)))
        for r in rows:
            print("    [%s] %s" % (r["relation_type"], r["resolved_path"]))

# ── Q4: All threshold constants (symbols) ─────────────────────────────────────
print("\n=== Q4: THRESHOLD CONSTANT SYMBOLS ===")
THRESHOLD_SYMS = [
    "HEALING_CONFIDENCE_X",
    "HEALING_CONFIDENCE_Y",
    "SCORE_THRESHOLD_DET",
    "SCORE_THRESHOLD_QWEN",
    "SOVEREIGN_HIGH_CONFIDENCE",
    "SOVEREIGN_MEDIUM_CONFIDENCE",
]
for sym in THRESHOLD_SYMS:
    cur.execute(
        "SELECT adg_name, entity_type, resolved_path FROM nodes "
        "WHERE adg_name LIKE ? AND entity_type='symbol' "
        "AND resolved_path NOT LIKE '%archive%'",
        ("%" + sym + "%",),
    )
    rows = cur.fetchall()
    if rows:
        print("  %s: defined in %d nodes" % (sym, len(rows)))
        for r in rows:
            print("    path=%-60s  name=%s" % (str(r["resolved_path"])[:60], r["adg_name"]))

# ── Q5: All importers of heal_policy_types ────────────────────────────────────
print("\n=== Q5: ALL IMPORTERS OF heal_policy_types ===")
cur.execute(
    "SELECT id FROM nodes WHERE resolved_path LIKE '%heal_policy_types%' "
    "AND entity_type='module' AND resolved_path NOT LIKE '%archive%'",
)
hpt_ids = [r[0] for r in cur.fetchall()]
if hpt_ids:
    ph = ",".join("?" * len(hpt_ids))
    cur.execute(
        "SELECT DISTINCT n_src.resolved_path, e.relation_type FROM edges e "
        "JOIN nodes n_src ON e.src_id=n_src.id "
        "WHERE e.dst_id IN (%s) AND n_src.resolved_path NOT LIKE '%%archive%%' "
        "ORDER BY n_src.resolved_path" % ph,
        hpt_ids,
    )
    for r in cur.fetchall():
        print("  [%s] %s" % (r["relation_type"], r["resolved_path"]))

# ── Q6: All importers of _ssot_routing ────────────────────────────────────────
print("\n=== Q6: ALL IMPORTERS OF _ssot_routing ===")
cur.execute(
    "SELECT id FROM nodes WHERE resolved_path LIKE '%_ssot_routing%' "
    "AND entity_type='module' AND resolved_path NOT LIKE '%archive%'",
)
sr_ids = [r[0] for r in cur.fetchall()]
if sr_ids:
    ph = ",".join("?" * len(sr_ids))
    cur.execute(
        "SELECT DISTINCT n_src.resolved_path, e.relation_type FROM edges e "
        "JOIN nodes n_src ON e.src_id=n_src.id "
        "WHERE e.dst_id IN (%s) AND n_src.resolved_path NOT LIKE '%%archive%%' "
        "ORDER BY n_src.resolved_path" % ph,
        sr_ids,
    )
    for r in cur.fetchall():
        print("  [%s] %s" % (r["relation_type"], r["resolved_path"]))

# ── Q7: routes_through / proposal_commits_routing edges ──────────────────────
print("\n=== Q7: routes_through + proposal_commits_routing EDGES ===")
for ek in ("routes_through", "proposal_commits_routing", "routing_commit", "path_route"):
    cur.execute("SELECT COUNT(*) FROM edges WHERE edge_kind=?", (ek,))
    cnt = cur.fetchone()[0]
    print("  %s: %d edges" % (ek, cnt))
    if cnt > 0 and cnt <= 20:
        cur.execute(
            "SELECT e.symbol, n_src.resolved_path, n_dst.resolved_path "
            "FROM edges e "
            "JOIN nodes n_src ON e.src_id=n_src.id "
            "JOIN nodes n_dst ON e.dst_id=n_dst.id "
            "WHERE e.edge_kind=? AND n_src.resolved_path NOT LIKE '%archive%' "
            "LIMIT 20",
            (ek,),
        )
        for r in cur.fetchall():
            print("    sym=%-40s  %s -> %s" % (str(r[0])[:40], r[1], r[2]))

# ── Q8: All reads_env in routing files ────────────────────────────────────────
print("\n=== Q8: reads_env IN ROUTING FILES ===")
cur.execute(
    "SELECT e.symbol, n_src.resolved_path FROM edges e "
    "JOIN nodes n_src ON e.src_id=n_src.id "
    "WHERE e.relation_type='reads_env' "
    "AND n_src.resolved_path NOT LIKE '%archive%' AND n_src.resolved_path NOT LIKE '%test%'",
)
envs = [r for r in cur.fetchall() if any(f in (r["resolved_path"] or "") for f in ROUTING_FRAGMENTS)]
for r in envs:
    print("  sym=%-40s  file=%s" % (str(r["symbol"])[:40], r["resolved_path"]))

# ── Q9: ConfidenceScore importers (production only) ──────────────────────────
print("\n=== Q9: ConfidenceScore PRODUCTION IMPORTERS ===")
cur.execute(
    "SELECT id FROM nodes WHERE adg_name LIKE '%ConfidenceScore%' "
    "AND entity_type='symbol' AND resolved_path NOT LIKE '%archive%' "
    "AND resolved_path LIKE '%_ssot_types%'",
)
cs_ids = [r[0] for r in cur.fetchall()]
if cs_ids:
    ph = ",".join("?" * len(cs_ids))
    cur.execute(
        "SELECT DISTINCT n_src.resolved_path FROM edges e "
        "JOIN nodes n_src ON e.src_id=n_src.id "
        "WHERE e.dst_id IN (%s) AND e.relation_type='imports' "
        "AND n_src.resolved_path NOT LIKE '%%archive%%' "
        "AND n_src.resolved_path NOT LIKE '%%test%%' "
        "ORDER BY n_src.resolved_path" % ph,
        cs_ids,
    )
    for r in cur.fetchall():
        print("  %s" % r[0])

# ── Q10: All HealingInput importers (production only) ─────────────────────────
print("\n=== Q10: HealingInput PRODUCTION IMPORTERS ===")
cur.execute(
    "SELECT id FROM nodes WHERE adg_name LIKE '%HealingInput%' "
    "AND entity_type='symbol' AND resolved_path NOT LIKE '%archive%' "
    "AND resolved_path NOT LIKE '%test%'",
)
hi_ids = [r[0] for r in cur.fetchall()]
if hi_ids:
    ph = ",".join("?" * len(hi_ids))
    cur.execute(
        "SELECT DISTINCT n_src.resolved_path FROM edges e "
        "JOIN nodes n_src ON e.src_id=n_src.id "
        "WHERE e.dst_id IN (%s) AND e.relation_type='imports' "
        "AND n_src.resolved_path NOT LIKE '%%archive%%' "
        "AND n_src.resolved_path NOT LIKE '%%test%%' "
        "ORDER BY n_src.resolved_path" % ph,
        hi_ids,
    )
    for r in cur.fetchall():
        print("  %s" % r[0])

# ── Q11: Hardcoded routing literals (antipattern edges) ───────────────────────
print("\n=== Q11: ANTIPATTERN EDGES TOTAL BREAKDOWN ===")
cur.execute(
    "SELECT e.symbol, COUNT(*) cnt FROM edges e "
    "WHERE e.edge_kind='antipattern' GROUP BY e.symbol ORDER BY cnt DESC LIMIT 30",
)
for r in cur.fetchall():
    print("  %-50s: %d" % (str(r[0] or "(null)")[:50], r[1]))

# ── Q12: Dead import edges in routing files ───────────────────────────────────
print("\n=== Q12: DEAD IMPORTS IN ROUTING FILES ===")
cur.execute(
    "SELECT e.symbol, n_src.resolved_path FROM edges e "
    "JOIN nodes n_src ON e.src_id=n_src.id "
    "WHERE e.edge_kind='dead_import' "
    "AND n_src.resolved_path NOT LIKE '%archive%'",
)
dead = [r for r in cur.fetchall() if any(f in (r["resolved_path"] or "") for f in ROUTING_FRAGMENTS)]
print("  count: %d" % len(dead))
for r in dead:
    print("  sym=%-50s  file=%s" % (str(r["symbol"])[:50], r["resolved_path"]))

# ── Q13: Full import chain: what does healing_tier_dispatcher import? ─────────
print("\n=== Q13: healing_tier_dispatcher IMPORTS ===")
cur.execute(
    "SELECT id FROM nodes WHERE resolved_path LIKE '%healing_tier_dispatcher%' "
    "AND entity_type='module' AND resolved_path NOT LIKE '%archive%'",
)
disp_ids = [r["id"] for r in cur.fetchall()]
for nid in disp_ids:
    cur.execute(
        "SELECT e.symbol, n_dst.resolved_path FROM edges e "
        "JOIN nodes n_dst ON e.dst_id=n_dst.id "
        "WHERE e.src_id=? AND e.relation_type='imports' "
        "AND n_dst.resolved_path NOT LIKE '%archive%' ORDER BY n_dst.resolved_path",
        (nid,),
    )
    for r in cur.fetchall():
        if r["resolved_path"]:
            print("  sym=%-60s  dst=%s" % (str(r["symbol"])[:60], r["resolved_path"]))

# ── Q14: SovereignBaseAgent imports ───────────────────────────────────────────
print("\n=== Q14: SovereignBaseAgent ROUTING IMPORTS ===")
cur.execute(
    "SELECT id FROM nodes WHERE resolved_path LIKE '%SovereignBaseAgent%' "
    "AND entity_type='module' AND resolved_path NOT LIKE '%archive%'",
)
sba_ids = [r["id"] for r in cur.fetchall()]
for nid in sba_ids:
    cur.execute(
        "SELECT e.symbol, n_dst.resolved_path FROM edges e "
        "JOIN nodes n_dst ON e.dst_id=n_dst.id "
        "WHERE e.src_id=? AND e.relation_type='imports' "
        "AND (n_dst.resolved_path LIKE '%heal%' OR n_dst.resolved_path LIKE '%routing%' "
        "     OR n_dst.resolved_path LIKE '%ssot%' OR e.symbol LIKE '%confidence%' "
        "     OR e.symbol LIKE '%Heal%' OR e.symbol LIKE '%route%' OR e.symbol LIKE '%Route%') "
        "ORDER BY n_dst.resolved_path",
        (nid,),
    )
    for r in cur.fetchall():
        print("  sym=%-60s  dst=%s" % (str(r["symbol"])[:60], r["resolved_path"] or "(external)"))

# ── Q15: decorators_util routing imports ──────────────────────────────────────
print("\n=== Q15: decorators_util ROUTING IMPORTS ===")
cur.execute(
    "SELECT id FROM nodes WHERE resolved_path LIKE '%decorators_util%' "
    "AND entity_type='module' AND resolved_path NOT LIKE '%archive%'",
)
dec_ids = [r["id"] for r in cur.fetchall()]
for nid in dec_ids:
    cur.execute(
        "SELECT e.symbol, n_dst.resolved_path FROM edges e "
        "JOIN nodes n_dst ON e.dst_id=n_dst.id "
        "WHERE e.src_id=? AND e.relation_type='imports' "
        "AND (e.symbol LIKE '%Heal%' OR e.symbol LIKE '%route%' OR e.symbol LIKE '%Route%' "
        "     OR e.symbol LIKE '%confidence%' OR e.symbol LIKE '%score%') "
        "ORDER BY e.symbol",
        (nid,),
    )
    for r in cur.fetchall():
        print("  sym=%-60s  dst=%s" % (str(r["symbol"])[:60], r["resolved_path"] or "(external)"))

# ── Q16: RoutingTier vs HealingTier — who uses them ──────────────────────────
print("\n=== Q16: RoutingTier vs HealingTier IMPORTERS (prod) ===")
for sym in ("RoutingTier", "HealingTier"):
    cur.execute(
        "SELECT id FROM nodes WHERE adg_name LIKE ? AND entity_type='symbol' "
        "AND resolved_path NOT LIKE '%archive%'",
        ("%" + sym + "%",),
    )
    sym_ids = [r[0] for r in cur.fetchall()]
    if sym_ids:
        ph = ",".join("?" * len(sym_ids))
        cur.execute(
            "SELECT DISTINCT n_src.resolved_path FROM edges e "
            "JOIN nodes n_src ON e.src_id=n_src.id "
            "WHERE e.dst_id IN (%s) AND e.relation_type='imports' "
            "AND n_src.resolved_path NOT LIKE '%%archive%%' "
            "AND n_src.resolved_path NOT LIKE '%%test%%' "
            "ORDER BY n_src.resolved_path" % ph,
            sym_ids,
        )
        rows = cur.fetchall()
        print("  %s (%d prod importers):" % (sym, len(rows)))
        for r in rows:
            print("    %s" % r[0])

# ── Q17: Healing orchestration edges ─────────────────────────────────────────
print("\n=== Q17: orchestrates_healing + dispatches_healing_run EDGES (sample) ===")
for ek in ("orchestrates_healing", "dispatches_healing_run", "healer_action"):
    cur.execute("SELECT COUNT(*) FROM edges WHERE edge_kind=?", (ek,))
    cnt = cur.fetchone()[0]
    print("  %s: %d" % (ek, cnt))
    if 0 < cnt <= 10:
        cur.execute(
            "SELECT e.symbol, n_src.resolved_path FROM edges e "
            "JOIN nodes n_src ON e.src_id=n_src.id "
            "WHERE e.edge_kind=? AND n_src.resolved_path NOT LIKE '%archive%' LIMIT 10",
            (ek,),
        )
        for r in cur.fetchall():
            print("    %s  [%s]" % (r["resolved_path"], r["symbol"]))

db.close()
print("\nDONE.")
