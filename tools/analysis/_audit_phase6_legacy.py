"""
Phase 6: Legacy/Dead Code & Observability Gaps Audit — ADG GraphDB Technical Debt Audit.

Detects:
- Zero-caller modules (dead code with blast radius)
- Zero-caller symbols within active modules (dead symbols)
- Legacy naming patterns (deprecated, legacy, old, obsolete, compat)
- Orphan test files (tests for modules that no longer exist)
- Observability gaps (modules with no L6 edges, no trace/span emission)
- Unreachable modules (no import path from any entry point)
- Archive leakage (imports from archives/ in production code)

Read-only. No code modifications.
"""

# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"

import json
import sqlite3
from pathlib import Path
from collections import defaultdict

DB = Path(r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_04252026_0521.sqlite")
OUT = Path(r"C:\Git\Agentic-Workflow\artifacts\audit_phase6_legacy.json")

DEP_RELATIONS = (
    'imports', 'calls', 'references', 'flows_to', 'controls_flow',
    'writes_to', 'reads_from', 'invokes_provider', 'invokes_dynamic',
    'routes_through', 'retrieves_via', 'resolves_callsite',
    'emits_side_effect', 'applies', 'instantiates'
)


def q1_zero_caller_modules(cur: sqlite3.Cursor) -> list[dict]:
    """Modules with fan_in=0 — nothing imports them. Dead code."""
    cur.execute(
        "SELECT h.node_id, h.adg_name, h.layer, h.resolved_path, "
        "       h.fan_in, h.fan_out, h.betweenness_approx "
        "FROM mv_hotspot_centrality h "
        "WHERE h.fan_in = 0 AND h.fan_out > 0 "
        "  AND h.resolved_path NOT LIKE 'tests/%' "
        "  AND h.resolved_path NOT LIKE 'docs/archive/windsurf/legacy-tree/%' "
        "ORDER BY h.fan_out DESC "
        "LIMIT 100"
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q2_zero_caller_test_modules(cur: sqlite3.Cursor) -> list[dict]:
    """Test modules with fan_in=0 — potentially orphaned tests."""
    cur.execute(
        "SELECT h.node_id, h.adg_name, h.layer, h.resolved_path, "
        "       h.fan_in, h.fan_out "
        "FROM mv_hotspot_centrality h "
        "WHERE h.fan_in = 0 "
        "  AND h.resolved_path LIKE 'tests/%' "
        "ORDER BY h.fan_out DESC "
        "LIMIT 50"
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q3_legacy_naming(cur: sqlite3.Cursor) -> list[dict]:
    """Modules/symbols with legacy naming patterns (deprecated, legacy, old, obsolete, compat, _v1, _v2)."""
    cur.execute(
        "SELECT n.id, n.adg_name, n.layer, n.resolved_path, n.entity_type, "
        "       h.fan_in, h.fan_out "
        "FROM nodes n "
        "LEFT JOIN mv_hotspot_centrality h ON h.node_id = n.id "
        "WHERE (n.adg_name LIKE '%deprecated%' OR n.adg_name LIKE '%Deprecated%' "
        "       OR n.adg_name LIKE '%legacy%' OR n.adg_name LIKE '%Legacy%' "
        "       OR n.adg_name LIKE '%obsolete%' OR n.adg_name LIKE '%Obsolete%' "
        "       OR n.adg_name LIKE '%_old%' OR n.adg_name LIKE '%_v1%' "
        "       OR n.adg_name LIKE '%_v2%' OR n.adg_name LIKE '%compat%' "
        "       OR n.adg_name LIKE '%Compat%' OR n.adg_name LIKE '%shim%' "
        "       OR n.adg_name LIKE '%Shim%' OR n.adg_name LIKE '%_bak%' "
        "       OR n.adg_name LIKE '%_backup%' OR n.adg_name LIKE '%_tmp%') "
        "  AND n.entity_type IN ('module', 'symbol') "
        "  AND n.layer IS NOT NULL AND n.layer != '' "
        "ORDER BY COALESCE(h.fan_in, 0) DESC "
        "LIMIT 100"
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q4_observability_gaps(cur: sqlite3.Cursor) -> list[dict]:
    """Modules with no L6/observability edges — no trace emission, no span creation.
    These modules run silently without any observability coverage."""
    cur.execute(
        "SELECT n.id, n.adg_name, n.layer, n.resolved_path, "
        "       h.fan_in, h.fan_out "
        "FROM nodes n "
        "JOIN mv_hotspot_centrality h ON h.node_id = n.id "
        "WHERE n.entity_type = 'module' "
        "  AND n.layer IN ('L0', 'L1', 'L2', 'L3', 'L4', 'L5') "
        "  AND n.resolved_path NOT LIKE 'tests/%' "
        "  AND n.resolved_path NOT LIKE 'docs/archive/windsurf/legacy-tree/%' "
        "  AND n.id NOT IN ("
        "      SELECT DISTINCT e.src_id FROM edges e "
        "      JOIN nodes dst ON dst.id = e.dst_id "
        "      WHERE (e.relation_type IN ('emits_side_effect', 'writes_to') "
        "             AND (dst.adg_name LIKE '%trace%' OR dst.adg_name LIKE '%span%' "
        "                  OR dst.adg_name LIKE '%otel%' OR dst.adg_name LIKE '%audit%' "
        "                  OR dst.adg_name LIKE '%observ%' OR dst.adg_name LIKE '%metric%')) "
        "         OR e.relation_type = 'flows_to' AND dst.layer = 'L6' "
        "  ) "
        "  AND h.fan_in >= 5 "
        "ORDER BY h.fan_in DESC "
        "LIMIT 50"
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q5_archive_import_leakage(cur: sqlite3.Cursor) -> list[dict]:
    """Production code importing from archives/ — forbidden by constitutional rule."""
    cur.execute(
        "SELECT e.id AS edge_id, "
        "       src_n.adg_name AS importer, "
        "       src_n.layer AS importer_layer, "
        "       src_n.resolved_path AS importer_file, "
        "       dst_n.adg_name AS archive_module, "
        "       dst_n.resolved_path AS archive_file, "
        "       e.relation_type, e.source_file, e.line_no "
        "FROM edges e "
        "JOIN nodes src_n ON src_n.id = e.src_id "
        "JOIN nodes dst_n ON dst_n.id = e.dst_id "
        "WHERE e.relation_type = 'imports' "
        "  AND dst_n.resolved_path LIKE 'archives/%' "
        "  AND src_n.resolved_path NOT LIKE 'archives/%' "
        "  AND src_n.resolved_path NOT LIKE 'tests/%' "
        "ORDER BY src_n.layer "
        "LIMIT 100"
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q6_unreachable_from_entry(cur: sqlite3.Cursor) -> list[dict]:
    """Modules not reachable from any known entry point (composition_root, __main__, governed_*_run).
    Uses reverse BFS from entry points via edges table."""
    # Step 1: Find entry point modules
    cur.execute(
        "SELECT DISTINCT n.id, n.resolved_path FROM nodes n "
        "WHERE n.entity_type = 'module' "
        "  AND (n.resolved_path LIKE '%composition_root%' "
        "       OR n.resolved_path LIKE '%__main__%' "
        "       OR n.resolved_path LIKE '%governed_%_run%' "
        "       OR n.resolved_path LIKE '%_ingress_runner%' "
        "       OR n.resolved_path LIKE '%bootstrap_runtime%') "
        "  AND n.resolved_path NOT LIKE 'tests/%' "
    )
    entry_points = cur.fetchall()

    if not entry_points:
        return []

    # Step 2: BFS from entry points through imports edges
    reachable = set()
    frontier = set(ep[0] for ep in entry_points)
    visited = set()

    for _ in range(10):  # max depth 10
        if not frontier:
            break
        visited.update(frontier)
        reachable.update(frontier)

        if not frontier:
            break

        placeholders = ','.join(['?'] * len(frontier))
        cur.execute(
            f"SELECT DISTINCT e.dst_id FROM edges e "
            f"WHERE e.src_id IN ({placeholders}) "
            f"AND e.relation_type = 'imports'",
            list(frontier)
        )
        next_frontier = set(r[0] for r in cur.fetchall()) - visited
        frontier = next_frontier

    reachable.update(visited)

    # Step 3: Find modules NOT in reachable set
    cur.execute(
        "SELECT n.id, n.adg_name, n.layer, n.resolved_path, "
        "       h.fan_in, h.fan_out "
        "FROM nodes n "
        "LEFT JOIN mv_hotspot_centrality h ON h.node_id = n.id "
        "WHERE n.entity_type = 'module' "
        "  AND n.id NOT IN ({}) ".format(','.join(['?'] * len(reachable)) if reachable else '0'),
        list(reachable) if reachable else []
    )
    unreachable = []
    for row in cur.fetchall():
        r = dict(zip([d[0] for d in cur.description], row))
        # Filter out test/archive/windsurf paths
        rp = r.get('resolved_path', '')
        if rp and not rp.startswith('tests/') and not rp.startswith('archives/') and not rp.startswith('docs/archive/windsurf/legacy-tree/'):
            unreachable.append(r)

    # Sort by fan_out descending (highest blast radius unreachable = worst)
    unreachable.sort(key=lambda x: -(x.get('fan_out') or 0))
    return unreachable[:50]


def q7_orphan_test_targets(cur: sqlite3.Cursor) -> list[dict]:
    """Test files that import modules which no longer exist or have zero callers.
    Indicates tests for dead code or tests that will never fail."""
    cur.execute(
        "SELECT DISTINCT test_n.resolved_path AS test_file, "
        "       test_n.layer AS test_layer, "
        "       dst_n.resolved_path AS target_file, "
        "       dst_n.layer AS target_layer, "
        "       h.fan_in AS target_fan_in "
        "FROM edges e "
        "JOIN nodes test_n ON test_n.id = e.src_id "
        "JOIN nodes dst_n ON dst_n.id = e.dst_id "
        "LEFT JOIN mv_hotspot_centrality h ON h.node_id = dst_n.id "
        "WHERE e.relation_type = 'imports' "
        "  AND test_n.resolved_path LIKE 'tests/%' "
        "  AND dst_n.resolved_path NOT LIKE 'tests/%' "
        "  AND dst_n.entity_type = 'module' "
        "  AND COALESCE(h.fan_in, 0) <= 1 "
        "ORDER BY test_n.resolved_path "
        "LIMIT 100"
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q8_dead_symbols_in_active_modules(cur: sqlite3.Cursor) -> list[dict]:
    """Symbols within active modules (fan_in > 0) that themselves have zero incoming edges.
    Dead code inside living modules."""
    placeholders = ','.join(['?'] * len(DEP_RELATIONS))
    cur.execute(
        "SELECT sym_n.id, sym_n.adg_name, sym_n.layer, sym_n.resolved_path, "
        "       mod_h.fan_in AS module_fan_in, mod_h.fan_out AS module_fan_out "
        "FROM nodes sym_n "
        "JOIN mv_hotspot_centrality mod_h ON mod_h.resolved_path = sym_n.resolved_path "
        "WHERE sym_n.entity_type = 'symbol' "
        "  AND sym_n.layer IS NOT NULL AND sym_n.layer != '' "
        "  AND sym_n.resolved_path NOT LIKE 'tests/%' "
        "  AND mod_h.fan_in >= 5 "
        "  AND sym_n.id NOT IN ("
        f"      SELECT DISTINCT e.dst_id FROM edges e "
        f"      WHERE e.relation_type IN ({placeholders}) "
        "  ) "
        "ORDER BY mod_h.fan_in DESC "
        "LIMIT 100",
        list(DEP_RELATIONS)
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q9_violation_disposition_untriaged(cur: sqlite3.Cursor) -> list[dict]:
    """Violations still marked 'untriaged' — technical debt not yet assessed."""
    cur.execute(
        "SELECT v.id, v.category, v.evidence, v.severity, v.file_path, "
        "       v.line_no, v.disposition, v.violation_class "
        "FROM violations v "
        "WHERE v.disposition = 'untriaged' "
        "ORDER BY v.severity, v.file_path "
        "LIMIT 200"
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q10_high_fanout_no_observability(cur: sqlite3.Cursor) -> list[dict]:
    """High fan-out modules with no observability edges — orchestrators running blind.
    Combines Phase 4 fan-out data with Phase 6 observability gap analysis."""
    cur.execute(
        "SELECT h.node_id, h.adg_name, h.layer, h.resolved_path, "
        "       h.fan_in, h.fan_out, h.betweenness_approx "
        "FROM mv_hotspot_centrality h "
        "WHERE h.fan_out >= 10 "
        "  AND h.layer IN ('L0', 'L1', 'L2', 'L3', 'L4', 'L5') "
        "  AND h.resolved_path NOT LIKE 'tests/%' "
        "  AND h.resolved_path NOT LIKE 'docs/archive/windsurf/legacy-tree/%' "
        "  AND h.node_id NOT IN ("
        "      SELECT DISTINCT e.src_id FROM edges e "
        "      JOIN nodes dst ON dst.id = e.dst_id "
        "      WHERE (e.relation_type IN ('emits_side_effect', 'writes_to') "
        "             AND (dst.adg_name LIKE '%trace%' OR dst.adg_name LIKE '%span%' "
        "                  OR dst.adg_name LIKE '%otel%' OR dst.adg_name LIKE '%audit%')) "
        "         OR e.relation_type = 'flows_to' AND dst.layer = 'L6' "
        "  ) "
        "ORDER BY h.fan_out DESC "
        "LIMIT 50"
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def flag_debt(rows: list[dict], category: str) -> list[dict]:
    """Add severity classification."""
    for r in rows:
        r["_audit_category"] = category
        fan_in = r.get("fan_in") or r.get("module_fan_in") or 0
        fan_out = r.get("fan_out") or r.get("module_fan_out") or 0
        target_fan_in = r.get("target_fan_in") or 0

        # Observability gap severity
        if category in ("q4_observability_gaps", "q10_high_fanout_no_observability"):
            if fan_in >= 50 or fan_out >= 20:
                r["_severity"] = "P0"
            elif fan_in >= 20 or fan_out >= 10:
                r["_severity"] = "P1"
            elif fan_in >= 5:
                r["_severity"] = "P2"
            else:
                r["_severity"] = "P3"
        # Dead code severity
        elif category in ("q1_zero_caller_modules", "q6_unreachable_from_entry"):
            if fan_out >= 50:
                r["_severity"] = "P0"
            elif fan_out >= 20:
                r["_severity"] = "P1"
            elif fan_out >= 5:
                r["_severity"] = "P2"
            else:
                r["_severity"] = "P3"
        # Archive leakage
        elif category == "q5_archive_import_leakage":
            r["_severity"] = "P1"  # Always P1 — constitutional violation
        # Legacy naming
        elif category == "q3_legacy_naming":
            if fan_in >= 20:
                r["_severity"] = "P1"
            elif fan_in >= 5:
                r["_severity"] = "P2"
            else:
                r["_severity"] = "P3"
        # Orphan tests
        elif category in ("q2_zero_caller_test_modules", "q7_orphan_test_targets"):
            r["_severity"] = "P2" if target_fan_in == 0 else "P3"
        # Dead symbols
        elif category == "q8_dead_symbols_in_active_modules":
            if fan_in >= 50:
                r["_severity"] = "P1"
            elif fan_in >= 10:
                r["_severity"] = "P2"
            else:
                r["_severity"] = "P3"
        # Untriaged violations
        elif category == "q9_violation_disposition_untriaged":
            sev = r.get("severity", "LOW")
            if sev == "CRITICAL":
                r["_severity"] = "P0"
            elif sev == "HIGH":
                r["_severity"] = "P1"
            elif sev == "MEDIUM":
                r["_severity"] = "P2"
            else:
                r["_severity"] = "P3"
        else:
            r["_severity"] = "P3"
    return rows


def main() -> None:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    cur = con.cursor()

    report: dict = {
        "phase": "6_legacy_observability_audit",
        "adg_snapshot": "04252026_0521",
        "queries": {},
    }

    queries = [
        ("q1_zero_caller_modules", q1_zero_caller_modules),
        ("q2_zero_caller_test_modules", q2_zero_caller_test_modules),
        ("q3_legacy_naming", q3_legacy_naming),
        ("q4_observability_gaps", q4_observability_gaps),
        ("q5_archive_import_leakage", q5_archive_import_leakage),
        ("q6_unreachable_from_entry", q6_unreachable_from_entry),
        ("q7_orphan_test_targets", q7_orphan_test_targets),
        ("q8_dead_symbols_in_active_modules", q8_dead_symbols_in_active_modules),
        ("q9_violation_disposition_untriaged", q9_violation_disposition_untriaged),
        ("q10_high_fanout_no_observability", q10_high_fanout_no_observability),
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

    report["summary"] = {
        f"{q}_count": len(rows)
        for q, rows in report["queries"].items()
    }
    report["summary"].update({
        f"{k}_findings": v for k, v in sev_counts.items()
    })

    con.close()

    OUT.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
