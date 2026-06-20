"""
Phase 4: Fan-Out Hotspot Audit — ADG GraphDB Technical Debt Audit.

Identifies orchestration gravity wells, cross-layer dispatchers,
provider/egress surfaces, write-path mutation surfaces, and
forbidden callee-layer boundary violations.

Read-only. No code modifications.
"""

# W6 ADG consumer mode declaration (per .codex/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import json
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

DB = REPO_ROOT / "artifacts" / "adg" / "adg_indexed_04252026_0521.sqlite"
OUT = REPO_ROOT / "artifacts" / "audit_phase4_fanout.json"

# Forbidden caller→callee layer pairs (same as Phase 3)
FORBIDDEN_LAYER_PAIRS: list[tuple[str, str]] = [
    ("L2", "L0"),
    ("L2", "L1"),
    ("L2", "L3"),
    ("L3", "L0"),
    ("L3", "L1"),
    ("L4", "L0"),
    ("L4", "L1"),
    ("L4", "L2"),
    ("L4", "L3"),
    ("L6", "L4"),
    ("L0", "L2"),
    ("L0", "L4"),
    ("L1", "L2"),
    ("L1", "L4"),
    ("L_APP", "L0"),
    ("L_APP", "L4"),
    ("L_INFRA", "L0"),
    ("L_OPS", "L4"),
]

# Relation types for dependency analysis
DEP_RELATIONS = (
    "imports",
    "calls",
    "references",
    "flows_to",
    "controls_flow",
    "writes_to",
    "reads_from",
    "invokes_provider",
    "invokes_dynamic",
    "routes_through",
    "retrieves_via",
    "resolves_callsite",
    "emits_side_effect",
    "applies",
    "instantiates",
)


def q1_top_symbols_fanout(cur: sqlite3.Cursor) -> list[dict]:
    """Top 50 symbols by fan_out from mv_hotspot_centrality."""
    cur.execute(
        "SELECT node_id, adg_name, layer, resolved_path, "
        "       fan_in, fan_out, degree, betweenness_approx, degree_centrality "
        "FROM mv_hotspot_centrality "
        "WHERE fan_out > 0 "
        "ORDER BY fan_out DESC LIMIT 50"
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q2_top_modules_fanout(cur: sqlite3.Cursor) -> list[dict]:
    """Top 50 modules by aggregated symbol fan_out within each file."""
    cur.execute(
        "SELECT n.resolved_path, n.layer, "
        "       SUM(h.fan_out) AS total_fan_out, "
        "       SUM(h.fan_in) AS total_fan_in, "
        "       COUNT(*) AS symbol_count "
        "FROM mv_hotspot_centrality h "
        "JOIN nodes n ON n.id = h.node_id "
        "WHERE h.fan_out > 0 "
        "GROUP BY n.resolved_path "
        "ORDER BY total_fan_out DESC LIMIT 50"
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q3_orchestration_fanout(cur: sqlite3.Cursor) -> list[dict]:
    """High fan-out symbols in orchestration/control layers (L3, L0, L_SHARED)."""
    cur.execute(
        "SELECT h.node_id, h.adg_name, h.layer, h.resolved_path, "
        "       h.fan_out, h.fan_in, h.betweenness_approx "
        "FROM mv_hotspot_centrality h "
        "WHERE h.fan_out >= 10 "
        "  AND h.layer IN ('L3', 'L0', 'L_SHARED', 'L_RUNTIME') "
        "ORDER BY h.fan_out DESC LIMIT 50"
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q4_provider_egress_fanout(cur: sqlite3.Cursor) -> list[dict]:
    """Symbols that invoke providers or emit side effects (egress surface)."""
    cur.execute(
        "SELECT DISTINCT src_n.id AS node_id, src_n.adg_name, src_n.layer, "
        "       src_n.resolved_path, src_n.entity_type, "
        "       COUNT(DISTINCT e.dst_id) AS egress_edge_count, "
        "       GROUP_CONCAT(DISTINCT e.relation_type) AS egress_relation_types "
        "FROM edges e "
        "JOIN nodes src_n ON src_n.id = e.src_id "
        "WHERE e.relation_type IN ("
        "    'invokes_provider', 'invokes_dynamic', 'emits_side_effect', "
        "    'writes_to', 'writes_through', 'controls_flow', 'routes_through'"
        ") "
        "GROUP BY src_n.id "
        "HAVING egress_edge_count >= 3 "
        "ORDER BY egress_edge_count DESC LIMIT 50"
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q5_write_path_fanout(cur: sqlite3.Cursor) -> list[dict]:
    """Symbols on write/mutation paths (writes_to, writes_through, commits_mutation_durable, etc.)."""
    cur.execute(
        "SELECT DISTINCT src_n.id AS node_id, src_n.adg_name, src_n.layer, "
        "       src_n.resolved_path, src_n.entity_type, "
        "       COUNT(DISTINCT e.dst_id) AS write_target_count, "
        "       GROUP_CONCAT(DISTINCT e.relation_type) AS write_relation_types "
        "FROM edges e "
        "JOIN nodes src_n ON src_n.id = e.src_id "
        "WHERE e.relation_type IN ("
        "    'writes_to', 'writes_through', 'commits_mutation_durable', "
        "    'claims_write_lock', 'generates_mutation_diff', "
        "    'propagates_policy_hash', 'promotes_future_run_change', "
        "    'stores_embedding', 'appends_hash_chain', 'appends_commit_receipt'"
        ") "
        "GROUP BY src_n.id "
        "HAVING write_target_count >= 2 "
        "ORDER BY write_target_count DESC LIMIT 50"
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q6_mixed_callee_layers(cur: sqlite3.Cursor) -> list[dict]:
    """High fan-out modules that dispatch to >=3 distinct callee layers.

    Uses edges directly (module-level src_id) because many callee nodes
    have empty layer strings that must be filtered out.
    """
    cur.execute(
        "SELECT src_n.resolved_path AS caller_file, "
        "       src_n.layer AS caller_layer, "
        "       COUNT(DISTINCT e.dst_id) AS distinct_callees, "
        "       COUNT(DISTINCT dst_n.layer) AS callee_layer_count, "
        "       GROUP_CONCAT(DISTINCT dst_n.layer) AS callee_layers "
        "FROM edges e "
        "JOIN nodes src_n ON src_n.id = e.src_id "
        "JOIN nodes dst_n ON dst_n.id = e.dst_id "
        "WHERE e.relation_type IN (%s) "
        "  AND src_n.entity_type = 'module' "
        "  AND dst_n.layer IS NOT NULL AND dst_n.layer != '' "
        "GROUP BY src_n.resolved_path "
        "HAVING COUNT(DISTINCT dst_n.layer) >= 3 "
        "ORDER BY COUNT(DISTINCT dst_n.layer) DESC, COUNT(DISTINCT e.dst_id) DESC "
        "LIMIT 50" % ",".join(["'%s'" % r for r in DEP_RELATIONS])
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q7_forbidden_callee_layers(cur: sqlite3.Cursor) -> list[dict]:
    """Fan-out nodes dispatching to forbidden callee layers.

    Uses symbol-level edges for precision, joins to centrality via resolved_path.
    """
    pair_clauses = []
    pair_params: list[str] = []
    for caller, callee in FORBIDDEN_LAYER_PAIRS:
        pair_clauses.append("(src_n.layer = ? AND dst_n.layer = ?)")
        pair_params.extend([caller, callee])

    where_clause = " OR ".join(pair_clauses)

    cur.execute(
        "SELECT e.id AS edge_id, "
        "       src_n.layer AS caller_layer, "
        "       src_n.adg_name AS caller_symbol, "
        "       src_n.resolved_path AS caller_file, "
        "       dst_n.layer AS callee_layer, "
        "       dst_n.adg_name AS callee_symbol, "
        "       dst_n.resolved_path AS callee_file, "
        "       e.relation_type, e.source_file, e.line_no, "
        "       centr.fan_out AS caller_module_fan_out, "
        "       centr.fan_in AS caller_module_fan_in "
        "FROM edges e "
        "JOIN nodes src_n ON src_n.id = e.src_id "
        "JOIN nodes dst_n ON dst_n.id = e.dst_id "
        "LEFT JOIN mv_hotspot_centrality centr "
        "    ON centr.resolved_path = src_n.resolved_path "
        "WHERE e.relation_type IN (%s) "
        "  AND (%s) "
        "ORDER BY centr.fan_out DESC LIMIT 200"
        % (",".join(["'%s'" % r for r in DEP_RELATIONS]), where_clause),
        pair_params,
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q8_orphan_high_fanout(cur: sqlite3.Cursor) -> list[dict]:
    """Modules with high fan_out but zero or low fan_in — potential dead orchestrators
    or one-shot scripts with wide blast radius."""
    cur.execute(
        "SELECT node_id, adg_name, layer, resolved_path, "
        "       fan_in, fan_out, degree, betweenness_approx "
        "FROM mv_hotspot_centrality "
        "WHERE fan_out >= 20 AND fan_in <= 2 "
        "ORDER BY fan_out DESC LIMIT 50"
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q9_betweenness_bottlenecks(cur: sqlite3.Cursor) -> list[dict]:
    """Top 30 nodes by betweenness centrality — structural bottlenecks."""
    cur.execute(
        "SELECT node_id, adg_name, layer, resolved_path, "
        "       fan_in, fan_out, betweenness_approx, degree_centrality "
        "FROM mv_hotspot_centrality "
        "WHERE betweenness_approx > 0 "
        "ORDER BY betweenness_approx DESC LIMIT 30"
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def flag_debt(rows: list[dict], category: str) -> list[dict]:
    """Add severity classification based on fan_out and risk heuristics."""
    for r in rows:
        r["_audit_category"] = category
        fan_out = (
            r.get("fan_out")
            or r.get("egress_edge_count")
            or r.get("write_target_count")
            or r.get("distinct_callees")
            or r.get("callee_layer_count")
            or 0
        )
        layer = r.get("layer") or r.get("caller_layer") or ""

        # Severity heuristics
        if fan_out >= 100 and layer in ("L0", "L3", "L5", "L_SHARED"):
            r["_severity"] = "P0"
        elif fan_out >= 50 or (fan_out >= 20 and layer in ("L0", "L3", "L5")):
            r["_severity"] = "P1"
        elif fan_out >= 10:
            r["_severity"] = "P2"
        else:
            r["_severity"] = "P3"
    return rows


def main() -> None:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    cur = con.cursor()

    report: dict = {
        "phase": "4_fanout_hotspot_audit",
        "adg_snapshot": "04252026_0521",
        "queries": {},
    }

    queries = [
        ("q1_top_symbols_fanout", q1_top_symbols_fanout),
        ("q2_top_modules_fanout", q2_top_modules_fanout),
        ("q3_orchestration_fanout", q3_orchestration_fanout),
        ("q4_provider_egress_fanout", q4_provider_egress_fanout),
        ("q5_write_path_fanout", q5_write_path_fanout),
        ("q6_mixed_callee_layers", q6_mixed_callee_layers),
        ("q7_forbidden_callee_layers", q7_forbidden_callee_layers),
        ("q8_orphan_high_fanout", q8_orphan_high_fanout),
        ("q9_betweenness_bottlenecks", q9_betweenness_bottlenecks),
    ]

    for name, fn in queries:
        print(f"{name} ...", flush=True)
        rows = fn(cur)
        rows = flag_debt(rows, name)
        report["queries"][name] = rows

    # Summary
    sev_counts = {"p0": 0, "p1": 0, "p2": 0, "p3": 0}
    for qname, rows in report["queries"].items():
        for r in rows:
            sev = r.get("_severity", "P3").lower()
            if sev in sev_counts:
                sev_counts[sev] += 1

    report["summary"] = {f"{q}_count": len(rows) for q, rows in report["queries"].items()}
    report["summary"].update({f"{k}_findings": v for k, v in sev_counts.items()})

    con.close()

    OUT.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
