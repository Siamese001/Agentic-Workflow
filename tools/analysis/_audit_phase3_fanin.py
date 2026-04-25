"""Phase 3: Fan-In Hotspot Audit — ADG GraphDB Technical Debt / SSOT / Hardcoding Audit.

Read-only. Writes structured JSON to artifacts/audit_phase3_fanin.json.

Queries:
  Q1  Top 50 symbols by fan-in (mv_hotspot_centrality)
  Q2  Top 50 modules (file-level) by aggregated fan-in
  Q3  Top 50 config symbols by fan-in
  Q4  Top 50 registry symbols by fan-in
  Q5  Top 50 legacy/deprecated symbols by fan-in
  Q6  Top fan-in nodes with mixed caller layers (≥3 distinct caller layers)
  Q7  Top fan-in nodes receiving calls from forbidden caller layers

Canonical authority rules (audit contracts from Phase 1):
  L0 may route only — must not be called by L2/L4 for execution
  L1 may reason/plan only — must not be called by L0/L2/L3 for retrieval
  L4 is authoritative state — must not be called directly by L0/L1/L2/L3 for writes
  L5 is cross-cutting policy — must not be bypassed by L0/L1/L2/L3
  L6 observes only — must not be called for mutation by L0-L5

Forbidden caller→callee layer pairs (derived):
  L2→L0  (execution must not route)
  L2→L1  (execution must not plan)
  L3→L0  (orchestration must not route directly)
  L4→L0  (state must not route)
  L4→L1  (state must not plan)
  L6→L4  (observability must not write state directly)
  L0→L2  (routing must not execute)
  L0→L4  (routing must not write state)
  L1→L2  (cognition must not execute)
  L1→L4  (cognition must not write state)
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

DB = Path(r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_04252026_0521.sqlite")
OUT = Path(r"C:\Git\Agentic-Workflow\artifacts\audit_phase3_fanin.json")

# Forbidden caller_layer → callee_layer pairs (gravity violations)
FORBIDDEN_LAYER_PAIRS: list[tuple[str, str]] = [
    # Gravity violations: lower layers must not depend on higher
    ("L2", "L0"),  # execution must not route
    ("L2", "L1"),  # execution must not plan
    ("L2", "L3"),  # execution must not orchestrate
    ("L3", "L0"),  # orchestration must not route directly
    ("L3", "L1"),  # orchestration must not plan
    ("L4", "L0"),  # state must not route
    ("L4", "L1"),  # state must not plan
    ("L4", "L2"),  # state must not execute
    ("L4", "L3"),  # state must not orchestrate
    ("L6", "L4"),  # observability must not write state directly
    # Reverse gravity: higher layers must not reach into lower internals
    ("L0", "L2"),  # routing must not execute
    ("L0", "L4"),  # routing must not write state
    ("L1", "L2"),  # cognition must not execute
    ("L1", "L4"),  # cognition must not write state
    # Cross-domain: apps must not reach into core layers directly
    ("L_APP", "L0"),  # apps bypassing routing
    ("L_APP", "L4"),  # apps bypassing UWG
    ("L_INFRA", "L0"),  # infra bypassing routing
    ("L_OPS", "L4"),  # ops bypassing UWG
]


def q1_top_symbols_fanin(cur: sqlite3.Cursor) -> list[dict]:
    """Top 50 symbols by fan_in from mv_hotspot_centrality."""
    cur.execute("""
        SELECT node_id, adg_name, layer, resolved_path,
               fan_in, fan_out, degree, betweenness_approx, degree_centrality
        FROM mv_hotspot_centrality
        WHERE fan_in > 0
        ORDER BY fan_in DESC
        LIMIT 50
    """)
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q2_top_modules_fanin(cur: sqlite3.Cursor) -> list[dict]:
    """Top 50 files by aggregated fan-in (sum of symbol fan_in per file)."""
    cur.execute("""
        SELECT resolved_path, layer,
               SUM(fan_in) AS agg_fan_in,
               SUM(fan_out) AS agg_fan_out,
               COUNT(*) AS symbol_count,
               MAX(fan_in) AS max_symbol_fan_in
        FROM mv_hotspot_centrality
        WHERE fan_in > 0 AND resolved_path IS NOT NULL
        GROUP BY resolved_path, layer
        ORDER BY agg_fan_in DESC
        LIMIT 50
    """)
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q3_config_symbols_fanin(cur: sqlite3.Cursor) -> list[dict]:
    """Top 50 config-related symbols by fan-in.
    Heuristic: entity_type contains 'config' or adg_name contains 'config'/'setting'/'env'."""
    cur.execute("""
        SELECT h.node_id, h.adg_name, h.layer, h.resolved_path,
               h.fan_in, h.fan_out, n.entity_type, n.identity_kind
        FROM mv_hotspot_centrality h
        JOIN nodes n ON n.id = h.node_id
        WHERE h.fan_in > 0
          AND (
            n.entity_type LIKE '%config%'
            OR h.adg_name LIKE '%config%'
            OR h.adg_name LIKE '%Config%'
            OR h.adg_name LIKE '%setting%'
            OR h.adg_name LIKE '%env%'
            OR h.adg_name LIKE '%ENV%'
            OR h.adg_name LIKE '%_CONF%'
            OR h.adg_name LIKE '%_CFG%'
          )
        ORDER BY h.fan_in DESC
        LIMIT 50
    """)
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q4_registry_symbols_fanin(cur: sqlite3.Cursor) -> list[dict]:
    """Top 50 registry-related symbols by fan-in.
    Heuristic: adg_name contains 'registry'/'register'/'catalog'/'provider_map'."""
    cur.execute("""
        SELECT h.node_id, h.adg_name, h.layer, h.resolved_path,
               h.fan_in, h.fan_out, n.entity_type, n.identity_kind
        FROM mv_hotspot_centrality h
        JOIN nodes n ON n.id = h.node_id
        WHERE h.fan_in > 0
          AND (
            h.adg_name LIKE '%registr%'
            OR h.adg_name LIKE '%Registr%'
            OR h.adg_name LIKE '%catalog%'
            OR h.adg_name LIKE '%Catalog%'
            OR h.adg_name LIKE '%provider_map%'
            OR h.adg_name LIKE '%ProviderMap%'
            OR h.adg_name LIKE '%_REG%'
            OR h.adg_name LIKE '%_MAP%'
          )
        ORDER BY h.fan_in DESC
        LIMIT 50
    """)
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q5_legacy_deprecated_fanin(cur: sqlite3.Cursor) -> list[dict]:
    """Top 50 legacy/deprecated symbols by fan-in.
    Heuristic: adg_name or resolved_path contains legacy/deprecated/old/v1/shim/compat."""
    cur.execute("""
        SELECT h.node_id, h.adg_name, h.layer, h.resolved_path,
               h.fan_in, h.fan_out, n.entity_type, n.identity_kind
        FROM mv_hotspot_centrality h
        JOIN nodes n ON n.id = h.node_id
        WHERE h.fan_in > 0
          AND (
            h.adg_name LIKE '%legacy%'
            OR h.adg_name LIKE '%Legacy%'
            OR h.adg_name LIKE '%LEGACY%'
            OR h.adg_name LIKE '%deprecated%'
            OR h.adg_name LIKE '%Deprecated%'
            OR h.adg_name LIKE '%DEPRECATED%'
            OR h.adg_name LIKE '%_old%'
            OR h.adg_name LIKE '%_OLD%'
            OR h.adg_name LIKE '%_v1%'
            OR h.adg_name LIKE '%_V1%'
            OR h.adg_name LIKE '%shim%'
            OR h.adg_name LIKE '%Shim%'
            OR h.adg_name LIKE '%compat%'
            OR h.adg_name LIKE '%Compat%'
            OR h.resolved_path LIKE '%/archive/%'
            OR h.resolved_path LIKE '%\\archive\\%'
            OR h.resolved_path LIKE '%/legacy/%'
            OR h.resolved_path LIKE '%\\legacy\\%'
            OR h.resolved_path LIKE '%/deprecated/%'
            OR h.resolved_path LIKE '%\\deprecated\\%'
          )
        ORDER BY h.fan_in DESC
        LIMIT 50
    """)
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q6_mixed_caller_layers(cur: sqlite3.Cursor) -> list[dict]:
    """Top fan-in nodes with ≥3 distinct caller layers (mixed gravity well).

    Key insight: mv_hotspot_centrality has module-level node_ids,
    but edges reference symbol-level node_ids.
    Join via resolved_path to bridge module→symbol.
    """
    cur.execute("""
        SELECT
            h.node_id,
            h.adg_name,
            h.layer AS callee_layer,
            h.resolved_path,
            h.fan_in,
            COUNT(DISTINCT src_n.layer) AS caller_layer_count,
            GROUP_CONCAT(DISTINCT src_n.layer) AS caller_layers
        FROM mv_hotspot_centrality h
        JOIN nodes sym ON sym.resolved_path = h.resolved_path AND sym.entity_type = 'symbol'
        JOIN edges e ON e.dst_id = sym.id
        JOIN nodes src_n ON src_n.id = e.src_id
        WHERE h.fan_in >= 5
          AND e.relation_type IN (
            'imports', 'calls', 'references', 'flows_to', 'controls_flow',
            'writes_to', 'reads_from', 'invokes_provider', 'invokes_dynamic',
            'routes_through', 'retrieves_via', 'resolves_callsite',
            'emits_side_effect', 'applies', 'instantiates'
        )
        GROUP BY h.node_id
        HAVING COUNT(DISTINCT src_n.layer) >= 3
        ORDER BY h.fan_in DESC
        LIMIT 50
    """)
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q7_forbidden_layer_calls(cur: sqlite3.Cursor) -> list[dict]:
    """Fan-in nodes receiving calls from forbidden caller layers.

    Uses symbol-level edges (not module-level) for precision.
    Joins to mv_hotspot_centrality via resolved_path for fan_in data.
    """
    pair_clauses = []
    pair_params: list[str] = []
    for caller, callee in FORBIDDEN_LAYER_PAIRS:
        pair_clauses.append("(src_n.layer = ? AND dst_n.layer = ?)")
        pair_params.extend([caller, callee])

    where_clause = " OR ".join(pair_clauses)

    cur.execute(
        f"""
        SELECT
            e.id AS edge_id,
            src_n.layer AS caller_layer,
            src_n.adg_name AS caller_symbol,
            src_n.resolved_path AS caller_file,
            dst_n.layer AS callee_layer,
            dst_n.adg_name AS callee_symbol,
            dst_n.resolved_path AS callee_file,
            e.relation_type,
            e.source_file,
            e.line_no,
            centr.fan_in AS callee_module_fan_in,
            centr.fan_out AS callee_module_fan_out
        FROM edges e
        JOIN nodes src_n ON src_n.id = e.src_id
        JOIN nodes dst_n ON dst_n.id = e.dst_id
        LEFT JOIN mv_hotspot_centrality centr
            ON centr.resolved_path = dst_n.resolved_path
        WHERE e.relation_type IN (
            'imports', 'calls', 'references', 'flows_to', 'controls_flow',
            'writes_to', 'reads_from', 'invokes_provider', 'invokes_dynamic',
            'routes_through', 'retrieves_via', 'resolves_callsite',
            'emits_side_effect', 'applies', 'instantiates'
        )
          AND ({where_clause})
        ORDER BY centr.fan_in DESC
        LIMIT 200
    """,
        pair_params,
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def flag_debt(rows: list[dict], category: str) -> list[dict]:
    """Add severity classification based on fan-in and risk heuristics."""
    for r in rows:
        fanin = r.get("fan_in") or r.get("agg_fan_in") or r.get("callee_fan_in") or 0
        layer = r.get("layer") or r.get("callee_layer") or ""
        # Severity heuristics
        if fanin >= 50 and layer in ("L0_routing", "L4_state", "L5_safety"):
            sev = "P0"
        elif fanin >= 30 or layer in ("L0_routing", "L4_state", "L5_safety"):
            sev = "P1"
        elif fanin >= 10:
            sev = "P2"
        else:
            sev = "P3"
        r["_audit_category"] = category
        r["_severity"] = sev
    return rows


def main() -> int:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    cur = con.cursor()
    cur.execute("PRAGMA query_only = ON")

    print("Q1: top symbols by fan-in ...", file=sys.stderr)
    q1 = q1_top_symbols_fanin(cur)
    flag_debt(q1, "fanin_symbol_hotspot")

    print("Q2: top modules by fan-in ...", file=sys.stderr)
    q2 = q2_top_modules_fanin(cur)
    flag_debt(q2, "fanin_module_hotspot")

    print("Q3: config symbols by fan-in ...", file=sys.stderr)
    q3 = q3_config_symbols_fanin(cur)
    flag_debt(q3, "fanin_config_gravity")

    print("Q4: registry symbols by fan-in ...", file=sys.stderr)
    q4 = q4_registry_symbols_fanin(cur)
    flag_debt(q4, "fanin_registry_gravity")

    print("Q5: legacy/deprecated by fan-in ...", file=sys.stderr)
    q5 = q5_legacy_deprecated_fanin(cur)
    flag_debt(q5, "fanin_legacy_active")

    print("Q6: mixed caller layers ...", file=sys.stderr)
    q6 = q6_mixed_caller_layers(cur)
    flag_debt(q6, "fanin_mixed_gravity_well")

    print("Q7: forbidden layer calls ...", file=sys.stderr)
    q7 = q7_forbidden_layer_calls(cur)
    flag_debt(q7, "fanin_boundary_violation")

    con.close()

    report = {
        "phase": "3_fanin_hotspot_audit",
        "adg_snapshot": "04252026_0521",
        "queries": {
            "q1_top_symbols_fanin": q1,
            "q2_top_modules_fanin": q2,
            "q3_config_symbols_fanin": q3,
            "q4_registry_symbols_fanin": q4,
            "q5_legacy_deprecated_fanin": q5,
            "q6_mixed_caller_layers": q6,
            "q7_forbidden_layer_calls": q7,
        },
        "summary": {
            "q1_count": len(q1),
            "q2_count": len(q2),
            "q3_count": len(q3),
            "q4_count": len(q4),
            "q5_count": len(q5),
            "q6_count": len(q6),
            "q7_count": len(q7),
            "p0_findings": sum(1 for r in q1 + q2 + q3 + q4 + q5 + q6 + q7 if r.get("_severity") == "P0"),
            "p1_findings": sum(1 for r in q1 + q2 + q3 + q4 + q5 + q6 + q7 if r.get("_severity") == "P1"),
            "p2_findings": sum(1 for r in q1 + q2 + q3 + q4 + q5 + q6 + q7 if r.get("_severity") == "P2"),
            "p3_findings": sum(1 for r in q1 + q2 + q3 + q4 + q5 + q6 + q7 if r.get("_severity") == "P3"),
        },
    }

    OUT.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
