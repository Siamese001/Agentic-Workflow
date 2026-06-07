"""
Phase 5: SSOT Violations & Hardcoding Audit — ADG GraphDB Technical Debt Audit.

Detects:
- Multiple source-of-truth for same concept (duplicate symbol definitions)
- Non-intentional hardcoding (magic paths/strings bypassing registries)
- Config/env/registry drift (stale references, orphan configs)
- Canonical authority violations (layer authority breaches)
- Cross-layer type redefinitions (same type defined in multiple layers)

Read-only. No code modifications.
"""

# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"

import json
import sqlite3
import re
from pathlib import Path
from collections import Counter

DB = Path(r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_04252026_0521.sqlite")
OUT = Path(r"C:\Git\Agentic-Workflow\artifacts\audit_phase5_ssot.json")

DEP_RELATIONS = (
    'imports', 'calls', 'references', 'flows_to', 'controls_flow',
    'writes_to', 'reads_from', 'invokes_provider', 'invokes_dynamic',
    'routes_through', 'retrieves_via', 'resolves_callsite',
    'emits_side_effect', 'applies', 'instantiates'
)


def q1_duplicate_symbol_names(cur: sqlite3.Cursor) -> list[dict]:
    """Symbols with the same short name defined in multiple files/layers.
    Indicates SSOT violation — same concept defined in multiple places.
    Short name = last component after the last '.' separator."""
    # Fetch all symbol names with layer info, then group in Python
    # because SQLite lacks reverse() for last-dot extraction.
    cur.execute(
        "SELECT adg_name, layer, resolved_path "
        "FROM nodes "
        "WHERE entity_type = 'symbol' "
        "  AND adg_name LIKE 'ADG::Symbol::%' "
        "  AND layer IS NOT NULL AND layer != '' "
    )
    rows = cur.fetchall()

    # Extract short name (last component after last dot, after removing ADG::Symbol::)
    from collections import defaultdict
    groups: dict[str, dict] = defaultdict(lambda: {"files": set(), "layers": set(), "adg_names": []})
    for adg_name, layer, resolved_path in rows:
        base = adg_name.replace("ADG::Symbol::", "")
        # Strip leading package prefixes (agentic_core., apps_*. etc)
        short = base.rsplit(".", 1)[-1] if "." in base else base
        if not short or short == "*":
            continue
        g = groups[short]
        g["files"].add(resolved_path)
        g["layers"].add(layer)
        g["adg_names"].append(adg_name)

    # Filter for >=3 distinct files
    results = []
    for short_name, g in sorted(groups.items(), key=lambda x: (-len(x[1]["files"]), -len(x[1]["layers"])))[:100]:
        if len(g["files"]) >= 3:
            results.append({
                "short_name": short_name,
                "file_count": len(g["files"]),
                "layer_count": len(g["layers"]),
                "layers": ",".join(sorted(g["layers"])),
                "files": ",".join(sorted(g["files"])[:10]),
            })
    return results


def q2_cross_layer_type_redefinition(cur: sqlite3.Cursor) -> list[dict]:
    """Types/classes defined in multiple layers — canonical authority violation.
    Each type should have exactly one authoritative layer.
    Uses Python-side grouping for last-dot extraction."""
    cur.execute(
        "SELECT adg_name, layer, resolved_path "
        "FROM nodes "
        "WHERE entity_type = 'symbol' "
        "  AND (adg_name LIKE '%Type%' OR adg_name LIKE '%Contract%' "
        "       OR adg_name LIKE '%Config%' OR adg_name LIKE '%Types%') "
        "  AND layer IS NOT NULL AND layer != '' "
    )
    rows = cur.fetchall()

    from collections import defaultdict
    groups: dict[str, dict] = defaultdict(lambda: {"files": set(), "layers": set()})
    for adg_name, layer, resolved_path in rows:
        base = adg_name.replace("ADG::Symbol::", "")
        short = base.rsplit(".", 1)[-1] if "." in base else base
        if not short or short == "*":
            continue
        g = groups[short]
        g["files"].add(resolved_path)
        g["layers"].add(layer)

    results = []
    for short_name, g in sorted(groups.items(), key=lambda x: (-len(x[1]["layers"]), -len(x[1]["files"])))[:100]:
        if len(g["layers"]) >= 2:
            results.append({
                "short_name": short_name,
                "layer_count": len(g["layers"]),
                "file_count": len(g["files"]),
                "layers": ",".join(sorted(g["layers"])),
                "files": ",".join(sorted(g["files"])[:10]),
            })
    return results


def q3_path_hardcoding_bypass(cur: sqlite3.Cursor) -> list[dict]:
    """Symbols that import from path_constants (canonical) AND have edges
    suggesting direct path references (potential hardcoding bypass)."""
    cur.execute(
        "SELECT n.id, n.adg_name, n.layer, n.resolved_path, "
        "       COUNT(DISTINCT e.dst_id) AS import_count, "
        "       GROUP_CONCAT(DISTINCT dst_n.adg_name) AS imported_symbols "
        "FROM nodes n "
        "JOIN edges e ON e.src_id = n.id "
        "JOIN nodes dst_n ON dst_n.id = e.dst_id "
        "WHERE e.relation_type = 'imports' "
        "  AND dst_n.resolved_path = 'agentic_core/L0_routing/config/path_constants.py' "
        "  AND n.entity_type = 'module' "
        "GROUP BY n.id "
        "ORDER BY import_count DESC "
        "LIMIT 50"
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q4_config_import_cross_layer(cur: sqlite3.Cursor) -> list[dict]:
    """Config imports that cross layer boundaries — config should flow through
    canonical injection, not direct cross-layer import."""
    cur.execute(
        "SELECT src_n.resolved_path AS importer_file, "
        "       src_n.layer AS importer_layer, "
        "       dst_n.resolved_path AS config_file, "
        "       dst_n.layer AS config_layer, "
        "       e.relation_type, e.source_file, e.line_no "
        "FROM edges e "
        "JOIN nodes src_n ON src_n.id = e.src_id "
        "JOIN nodes dst_n ON dst_n.id = e.dst_id "
        "WHERE e.relation_type = 'imports' "
        "  AND src_n.entity_type = 'module' "
        "  AND dst_n.entity_type = 'module' "
        "  AND (dst_n.resolved_path LIKE '%/config/%' "
        "       OR dst_n.resolved_path LIKE '%/config_%' "
        "       OR dst_n.resolved_path LIKE '%_config.py') "
        "  AND src_n.layer != dst_n.layer "
        "  AND src_n.layer IS NOT NULL AND src_n.layer != '' "
        "  AND dst_n.layer IS NOT NULL AND dst_n.layer != '' "
        "ORDER BY src_n.layer, dst_n.layer "
        "LIMIT 200"
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q5_registry_fanin_concentration(cur: sqlite3.Cursor) -> list[dict]:
    """Registry/catalog symbols with high fan-in — canonical SSOT nodes
    that everything depends on. Any drift here cascades widely."""
    cur.execute(
        "SELECT h.node_id, h.adg_name, h.layer, h.resolved_path, "
        "       h.fan_in, h.fan_out, h.betweenness_approx "
        "FROM mv_hotspot_centrality h "
        "WHERE (h.adg_name LIKE '%Registry%' OR h.adg_name LIKE '%registry%' "
        "       OR h.adg_name LIKE '%Catalog%' OR h.adg_name LIKE '%catalog%' "
        "       OR h.adg_name LIKE '%ProviderMap%' OR h.adg_name LIKE '%provider_map%') "
        "  AND h.fan_in >= 3 "
        "ORDER BY h.fan_in DESC "
        "LIMIT 50"
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q6_orphan_config_nodes(cur: sqlite3.Cursor) -> list[dict]:
    """Config modules with zero or very low fan-in — potentially dead/orphan
    config that nothing references (registry drift)."""
    cur.execute(
        "SELECT h.node_id, h.adg_name, h.layer, h.resolved_path, "
        "       h.fan_in, h.fan_out "
        "FROM mv_hotspot_centrality h "
        "WHERE (h.resolved_path LIKE '%/config/%' "
        "       OR h.resolved_path LIKE '%/config_%' "
        "       OR h.resolved_path LIKE '%_config.py') "
        "  AND h.fan_in <= 2 "
        "ORDER BY h.fan_out DESC "
        "LIMIT 50"
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q7_env_var_surface(cur: sqlite3.Cursor) -> list[dict]:
    """Symbols referencing environment variables (heuristic on name).
    Env vars should flow through config layer, not be read directly in execution."""
    cur.execute(
        "SELECT n.id, n.adg_name, n.layer, n.resolved_path, n.entity_type "
        "FROM nodes n "
        "WHERE (n.adg_name LIKE '%environ%' OR n.adg_name LIKE '%ENV_%' "
        "       OR n.adg_name LIKE '%os_environ%' OR n.adg_name LIKE '%getenv%') "
        "  AND n.layer NOT IN ('L0', 'L_SHARED', 'L_RUNTIME', 'L_INFRA') "
        "  AND n.layer IS NOT NULL AND n.layer != '' "
        "ORDER BY n.layer "
        "LIMIT 50"
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q8_violation_ssot_conflicts(cur: sqlite3.Cursor) -> list[dict]:
    """ADG violations that indicate SSOT conflicts — violations tagged with
    categories suggesting duplicate authority or missing canonical source."""
    cur.execute(
        "SELECT v.id, v.category, v.severity, v.file_path, "
        "       v.evidence, v.violation_class, v.disposition "
        "FROM violations v "
        "WHERE v.category IN ("
        "    'antipattern', 'mis_layered_infra', 'apps_direct_infra', "
        "    'write_bypass_uwg', 'zero_caller_infra', "
        "    'duplicated_adapters', 'isolated_experimental'"
        ") "
        "  OR v.evidence IN ("
        "    'broad_exception_catch', 'log_and_swallow', 'silent_exception_swallow', "
        "    'return_none_swallow', 'unused_import'"
        ") "
        "ORDER BY v.severity, v.file_path "
        "LIMIT 200"
    )
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def q9_pview_ssot_matches(cur: sqlite3.Cursor) -> list[dict]:
    """Check P-views for SSOT-relevant patterns:
    - v_p0_apps_direct_infra: apps bypassing core
    - v_p0_write_bypass_uwg: writes bypassing canonical write gateway
    - v_p1_mis_layered_infra: infrastructure in wrong layer
    - v_p1_zero_caller_infra: dead infrastructure
    - v_p2_duplicated_adapters: adapter duplication (SSOT violation)"""
    results = []
    pviews = [
        ('v_p0_apps_direct_infra', 'apps_bypass_core'),
        ('v_p0_write_bypass_uwg', 'write_bypass_uwg'),
        ('v_p1_mis_layered_infra', 'mis_layered_infra'),
        ('v_p1_zero_caller_infra', 'zero_caller_infra'),
        ('v_p2_duplicated_adapters', 'duplicated_adapters'),
        ('v_p3_isolated_experimental', 'isolated_experimental'),
    ]
    for view_name, category in pviews:
        try:
            cur.execute(f"SELECT * FROM {view_name} LIMIT 50")
            rows = [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]
            for r in rows:
                r['_pview'] = view_name
                r['_audit_category'] = category
            results.extend(rows)
        except Exception:
            pass  # View may not exist or be empty
    return results


def q10_authority_boundary_breaches(cur: sqlite3.Cursor) -> list[dict]:
    """Check mv_authority_boundary_breaches for canonical authority violations."""
    try:
        cur.execute(
            "SELECT * FROM mv_authority_boundary_breaches LIMIT 100"
        )
        return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]
    except Exception:
        return []


def flag_debt(rows: list[dict], category: str) -> list[dict]:
    """Add severity classification."""
    for r in rows:
        r["_audit_category"] = category
        # Heuristics based on SSOT risk
        layer_count = r.get("layer_count") or r.get("file_count") or 0
        fan_in = r.get("fan_in") or 0
        layers = r.get("layers") or ""

        if layer_count >= 5 or fan_in >= 100:
            r["_severity"] = "P0"
        elif layer_count >= 3 or fan_in >= 20:
            r["_severity"] = "P1"
        elif layer_count >= 2 or fan_in >= 5:
            r["_severity"] = "P2"
        else:
            r["_severity"] = "P3"
    return rows


def main() -> None:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    cur = con.cursor()

    report: dict = {
        "phase": "5_ssot_hardcoding_audit",
        "adg_snapshot": "04252026_0521",
        "queries": {},
    }

    queries = [
        ("q1_duplicate_symbol_names", q1_duplicate_symbol_names),
        ("q2_cross_layer_type_redefinition", q2_cross_layer_type_redefinition),
        ("q3_path_hardcoding_bypass", q3_path_hardcoding_bypass),
        ("q4_config_import_cross_layer", q4_config_import_cross_layer),
        ("q5_registry_fanin_concentration", q5_registry_fanin_concentration),
        ("q6_orphan_config_nodes", q6_orphan_config_nodes),
        ("q7_env_var_surface", q7_env_var_surface),
        ("q8_violation_ssot_conflicts", q8_violation_ssot_conflicts),
        ("q9_pview_ssot_matches", q9_pview_ssot_matches),
        ("q10_authority_boundary_breaches", q10_authority_boundary_breaches),
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
