"""
Phases 1-2 + 8-16: Remaining ADG Technical Debt Audit phases.

Phase 1:  SSOT duplicate symbol short-names (extracted from Phase 5 Q1)
Phase 2:  Cross-layer type redefinition (extracted from Phase 5 Q2)
Phase 8:  Untriaged violation aging — gap vs CI dispositioning
Phase 9:  Observability blind spots on top-fan-in (>=50) modules — gap vs check_trace_stub_modules
Phase 10: Hardcoded external service literals (API versions, data-source IDs, base URLs)
Phase 11: Provider egress concentration — top-N modules calling external SDKs
Phase 12: Mixed-callee-layer dispatchers (>=4 distinct callee layers)
Phase 13: Cyclic / mutually-imported clusters between ACTIVE modules
Phase 14: Env var references in non-config layers (gap vs check_config_references)
Phase 15: Orphan config nodes (fan_in <= 1, fan_out >= 50) — gap vs check_dead_folder_detector
Phase 16: Final consolidated report — findings NOT covered by 94 ADG CI gates

Read-only. No code modifications.
"""

# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"

import json
import re
import sqlite3
from pathlib import Path
from collections import defaultdict, Counter

DB = Path(r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_04252026_0521.sqlite")
ART = Path(r"C:\Git\Agentic-Workflow\artifacts")

# CI gate coverage map — each entry maps (gate_name -> finding_categories it covers)
# Used by Phase 16 to filter out findings already covered by CI.
CI_COVERAGE = {
    "check_exception_contract": ["broad_catch", "exception_antipattern", "Exception", "AttributeError", "OSError", "ValueError", "KeyError", "ImportError", "RuntimeError", "TypeError"],
    "check_dead_methods_ratchet": ["dead_method", "unused_method"],
    "check_dead_symbols_ratchet": ["dead_symbol", "unused_symbol"],
    "check_dead_folder_detector": ["dead_folder", "orphan_folder"],
    "check_unused_imports_ratchet": ["unused_import"],
    "check_uwg_bypass_ratchet": ["uwg_bypass", "write_bypass"],
    "check_overlay_ratchet": ["overlay_drift"],
    "check_module_loc_ratchet": ["module_size"],
    "check_cyclomatic_ceiling": ["complexity"],
    "check_lpg_drift_ratchet": ["lpg_drift", "fanin_collapse"],
    "check_layer_skip": ["layer_skip", "layer_violation"],
    "check_structure_policy": ["structure_violation"],
    "check_hardcoded_exclusions": ["hardcoded_exclusion"],
    "check_config_references": ["config_reference"],
    "check_graph_island": ["graph_island", "isolated_node"],
    "check_graph_reach": ["unreachable", "graph_reach"],
    "check_trace_stub_modules": ["trace_stub", "stub_module"],
    "check_runtime_adg_coverage": ["runtime_coverage"],
    "check_w4_silent_writes": ["silent_write"],
    "check_w4_replay_surface_gaps": ["replay_surface_gap"],
    "check_w4_unresolved_callsites": ["unresolved_callsite"],
    "check_w6_fanin_collapse": ["fanin_collapse"],
    "check_w6_new_orphans_delta": ["new_orphan"],
    "check_w6_trace_theater_kpi": ["trace_theater"],
    "check_w5_broken_contract": ["broken_contract"],
    "check_w5_missing_adapter": ["missing_adapter"],
    "check_w5_taint_actionable": ["taint"],
    "check_w5_untyped_seam": ["untyped_seam"],
    "check_canonical_pipeline_wiring": ["pipeline_wiring"],
    "check_pipeline_skips": ["pipeline_skip"],
    "check_severity_band_ssot": ["severity_band_drift"],
    "check_baseline_staleness": ["baseline_staleness"],
    "check_snapshot_has_mvs": ["snapshot_mv_missing"],
    "check_graph_layer_evidence": ["plan_graph_evidence"],
    "check_graph_watchlist_delta": ["watchlist_drift"],
    "check_role_dedup": ["duplicate_role"],
}

# Findings categories that are NOT covered by any CI gate (manually curated)
UNCOVERED_CATEGORIES = {
    "ssot_duplicate_symbol_name",        # Phase 1 — magic constants in N layers
    "ssot_cross_layer_type_redefinition", # Phase 2 — types defined in N layers
    "untriaged_violation_aging",         # Phase 8 — disposition='untriaged' SLA
    "observability_blind_spot_high_fanin", # Phase 9 — fan_in>=50 with no L6 edges
    "hardcoded_external_service_literal", # Phase 10 — API versions, data source IDs
    "provider_egress_concentration",      # Phase 11 — external SDK call density
    "mixed_callee_layer_dispatcher",      # Phase 12 — orchestrator with >=4 callee layers
    "cyclic_active_cluster",              # Phase 13 — import cycles between living modules
    "env_var_outside_config_layer",       # Phase 14 — getenv/environ in non-L_CONFIG
    "orphan_config_with_blast_radius",    # Phase 15 — fan_in<=1, fan_out>=50 config
}


# ---------------------------------------------------------------------
# Phase 1 & 2 — extract from existing Phase 5 artifact
# ---------------------------------------------------------------------

def phase1_ssot_duplicate_symbol_names() -> dict:
    p5 = json.loads((ART / "audit_phase5_ssot.json").read_text(encoding="utf-8"))
    return {
        "phase": "1_ssot_duplicate_symbol_names",
        "description": "Symbols with same short_name defined in >=3 different files (extracted from Phase 5 Q1)",
        "category": "ssot_duplicate_symbol_name",
        "findings": p5["queries"]["q1_duplicate_symbol_names"],
    }


def phase2_cross_layer_type_redefinition() -> dict:
    p5 = json.loads((ART / "audit_phase5_ssot.json").read_text(encoding="utf-8"))
    return {
        "phase": "2_cross_layer_type_redefinition",
        "description": "Types/Configs/Contracts defined in >=2 different layers (extracted from Phase 5 Q2)",
        "category": "ssot_cross_layer_type_redefinition",
        "findings": p5["queries"]["q2_cross_layer_type_redefinition"],
    }


# ---------------------------------------------------------------------
# Phase 8 — Untriaged violation aging
# ---------------------------------------------------------------------

def phase8_untriaged_aging(cur: sqlite3.Cursor) -> dict:
    cur.execute("""
        SELECT category, severity, COUNT(*) as cnt,
               COUNT(DISTINCT file_path) as files,
               COUNT(DISTINCT evidence) as evidence_kinds
        FROM violations
        WHERE disposition = 'untriaged'
        GROUP BY category, severity
        ORDER BY cnt DESC
    """)
    by_severity = [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]

    cur.execute("""
        SELECT file_path, COUNT(*) as cnt
        FROM violations
        WHERE disposition = 'untriaged'
        GROUP BY file_path
        ORDER BY cnt DESC LIMIT 50
    """)
    top_files = [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]

    return {
        "phase": "8_untriaged_violation_aging",
        "description": "Violations with disposition='untriaged' grouped by category and file (no CI SLA gate)",
        "category": "untriaged_violation_aging",
        "by_severity": by_severity,
        "top_files": top_files,
    }


# ---------------------------------------------------------------------
# Phase 9 — Observability blind spots on top-fan-in modules
# ---------------------------------------------------------------------

def phase9_observability_blind_spots(cur: sqlite3.Cursor) -> dict:
    cur.execute("""
        SELECT n.id, n.adg_name, n.layer, n.resolved_path,
               h.fan_in, h.fan_out, h.betweenness_approx
        FROM nodes n
        JOIN mv_hotspot_centrality h ON h.node_id = n.id
        WHERE n.entity_type = 'module'
          AND h.fan_in >= 50
          AND n.layer IN ('L0','L1','L2','L3','L4','L5')
          AND n.resolved_path NOT LIKE 'tests/%'
          AND n.resolved_path NOT LIKE 'docs/archive/windsurf/legacy-tree/%'
          AND n.id NOT IN (
              SELECT DISTINCT e.src_id FROM edges e
              JOIN nodes dst ON dst.id = e.dst_id
              WHERE (e.relation_type IN ('emits_side_effect','writes_to','flows_to')
                     AND (dst.adg_name LIKE '%trace%' OR dst.adg_name LIKE '%span%'
                          OR dst.adg_name LIKE '%otel%' OR dst.adg_name LIKE '%audit%'
                          OR dst.adg_name LIKE '%observ%' OR dst.adg_name LIKE '%metric%'))
                 OR (e.relation_type = 'flows_to' AND dst.layer = 'L6')
          )
        ORDER BY h.fan_in DESC
        LIMIT 100
    """)
    findings = [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]
    return {
        "phase": "9_observability_blind_spots_high_fanin",
        "description": "Modules with fan_in >= 50 and zero L6/observability edges — blind hotspots",
        "category": "observability_blind_spot_high_fanin",
        "findings": findings,
    }


# ---------------------------------------------------------------------
# Phase 10 — Hardcoded external service literals
# ---------------------------------------------------------------------

EXTERNAL_LITERAL_PATTERNS = [
    "NOTION_API_VERSION", "NOTION_BASE", "WAVE_PHASE_DATA_SOURCE_ID",
    "anthropic.com", "openai.com", "googleapis.com", "vercel.com",
    "https://api.", "https://www.", "Bearer ", "sk-",
    "_DATA_SOURCE_ID", "_PAGE_ID",
]


def phase10_hardcoded_external_literals(cur: sqlite3.Cursor) -> dict:
    findings = []
    for pat in EXTERNAL_LITERAL_PATTERNS:
        cur.execute("""
            SELECT file_path, line_no, evidence, severity
            FROM violations
            WHERE evidence LIKE ?
              AND file_path NOT LIKE 'tests/%'
              AND file_path NOT LIKE '%scratch%'
            LIMIT 100
        """, (f"%{pat}%",))
        for r in cur.fetchall():
            findings.append({
                "file_path": r[0], "line_no": r[1],
                "evidence": r[2], "severity": r[3],
                "matched_pattern": pat,
            })

    return {
        "phase": "10_hardcoded_external_service_literals",
        "description": "API versions, data source IDs, base URLs hardcoded outside config (gap vs check_hardcoded_exclusions)",
        "category": "hardcoded_external_service_literal",
        "findings": findings,
        "patterns_searched": EXTERNAL_LITERAL_PATTERNS,
    }


# ---------------------------------------------------------------------
# Phase 11 — Provider egress concentration
# ---------------------------------------------------------------------

def phase11_provider_egress(cur: sqlite3.Cursor) -> dict:
    cur.execute("""
        SELECT src_n.resolved_path, src_n.layer,
               COUNT(*) as egress_count,
               COUNT(DISTINCT e.dst_id) as distinct_targets
        FROM edges e
        JOIN nodes src_n ON src_n.id = e.src_id
        JOIN nodes dst_n ON dst_n.id = e.dst_id
        WHERE e.relation_type IN ('imports','calls','invokes_provider','invokes_dynamic')
          AND (dst_n.adg_name LIKE '%anthropic%' OR dst_n.adg_name LIKE '%openai%'
               OR dst_n.adg_name LIKE '%google%' OR dst_n.adg_name LIKE '%vllm%'
               OR dst_n.adg_name LIKE '%httpx%' OR dst_n.adg_name LIKE '%requests%'
               OR dst_n.adg_name LIKE '%urllib%' OR dst_n.adg_name LIKE '%llm_judge%'
               OR dst_n.adg_name LIKE '%notion%' OR dst_n.adg_name LIKE '%qwen%')
          AND src_n.entity_type = 'module'
          AND src_n.resolved_path NOT LIKE 'tests/%'
        GROUP BY src_n.resolved_path, src_n.layer
        HAVING egress_count >= 3
        ORDER BY egress_count DESC
        LIMIT 100
    """)
    findings = [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]
    return {
        "phase": "11_provider_egress_concentration",
        "description": "Modules with concentrated calls to external providers/SDKs (no CI gate ranks egress)",
        "category": "provider_egress_concentration",
        "findings": findings,
    }


# ---------------------------------------------------------------------
# Phase 12 — Mixed-callee-layer dispatchers
# ---------------------------------------------------------------------

def phase12_mixed_callee_layers(cur: sqlite3.Cursor) -> dict:
    cur.execute("""
        SELECT src_n.resolved_path, src_n.layer,
               COUNT(DISTINCT dst_n.layer) as distinct_callee_layers,
               GROUP_CONCAT(DISTINCT dst_n.layer) as callee_layers,
               COUNT(*) as total_edges
        FROM edges e
        JOIN nodes src_n ON src_n.id = e.src_id
        JOIN nodes dst_n ON dst_n.id = e.dst_id
        WHERE e.relation_type IN ('imports','calls','flows_to','controls_flow')
          AND src_n.entity_type = 'module'
          AND src_n.layer IN ('L0','L1','L2','L3','L4','L5')
          AND dst_n.layer IS NOT NULL AND dst_n.layer != ''
          AND src_n.resolved_path NOT LIKE 'tests/%'
        GROUP BY src_n.resolved_path, src_n.layer
        HAVING distinct_callee_layers >= 4
        ORDER BY distinct_callee_layers DESC, total_edges DESC
        LIMIT 100
    """)
    findings = [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]
    return {
        "phase": "12_mixed_callee_layer_dispatchers",
        "description": "Modules dispatching to >=4 distinct callee layers (architectural blast pattern, not single-edge)",
        "category": "mixed_callee_layer_dispatcher",
        "findings": findings,
    }


# ---------------------------------------------------------------------
# Phase 13 — Cyclic clusters between active modules
# ---------------------------------------------------------------------

def phase13_cyclic_clusters(cur: sqlite3.Cursor) -> dict:
    """Detect 2-cycles: A imports B AND B imports A, where both have fan_in >= 1."""
    cur.execute("""
        SELECT
            n_a.resolved_path AS file_a, n_a.layer AS layer_a,
            n_b.resolved_path AS file_b, n_b.layer AS layer_b,
            ha.fan_in AS fan_in_a, hb.fan_in AS fan_in_b
        FROM edges e1
        JOIN edges e2 ON e2.src_id = e1.dst_id AND e2.dst_id = e1.src_id
        JOIN nodes n_a ON n_a.id = e1.src_id
        JOIN nodes n_b ON n_b.id = e1.dst_id
        JOIN mv_hotspot_centrality ha ON ha.node_id = n_a.id
        JOIN mv_hotspot_centrality hb ON hb.node_id = n_b.id
        WHERE e1.relation_type = 'imports' AND e2.relation_type = 'imports'
          AND n_a.entity_type = 'module' AND n_b.entity_type = 'module'
          AND n_a.id < n_b.id
          AND n_a.resolved_path NOT LIKE 'tests/%'
          AND n_b.resolved_path NOT LIKE 'tests/%'
          AND ha.fan_in >= 1 AND hb.fan_in >= 1
        ORDER BY ha.fan_in + hb.fan_in DESC
        LIMIT 100
    """)
    findings = [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]
    return {
        "phase": "13_cyclic_active_clusters",
        "description": "2-cycles between active modules (A imports B and B imports A, both fan_in>=1) — gap vs check_graph_island",
        "category": "cyclic_active_cluster",
        "findings": findings,
    }


# ---------------------------------------------------------------------
# Phase 14 — Env var references outside config layer
# ---------------------------------------------------------------------

def phase14_env_var_outside_config(cur: sqlite3.Cursor) -> dict:
    cur.execute("""
        SELECT n.id, n.adg_name, n.layer, n.resolved_path
        FROM nodes n
        WHERE (n.adg_name LIKE '%os.environ%' OR n.adg_name LIKE '%getenv%'
               OR n.adg_name LIKE '%ENV_%' OR n.adg_name LIKE '%_ENV%')
          AND n.layer IN ('L0','L1','L2','L3','L4','L5')
          AND n.resolved_path NOT LIKE '%/config/%'
          AND n.resolved_path NOT LIKE '%/config.py'
          AND n.resolved_path NOT LIKE 'tests/%'
        LIMIT 100
    """)
    findings = [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]
    return {
        "phase": "14_env_var_outside_config_layer",
        "description": "Env var references in production code outside config/ folder (gap vs check_config_references)",
        "category": "env_var_outside_config_layer",
        "findings": findings,
    }


# ---------------------------------------------------------------------
# Phase 15 — Orphan config with blast radius
# ---------------------------------------------------------------------

def phase15_orphan_config_blast(cur: sqlite3.Cursor) -> dict:
    cur.execute("""
        SELECT n.id, n.adg_name, n.layer, n.resolved_path,
               h.fan_in, h.fan_out
        FROM nodes n
        JOIN mv_hotspot_centrality h ON h.node_id = n.id
        WHERE n.entity_type = 'module'
          AND (n.resolved_path LIKE '%/config/%' OR n.resolved_path LIKE '%_config.py')
          AND h.fan_in <= 1
          AND h.fan_out >= 50
          AND n.resolved_path NOT LIKE 'tests/%'
          AND n.resolved_path NOT LIKE 'archives/%'
        ORDER BY h.fan_out DESC
        LIMIT 100
    """)
    findings = [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]
    return {
        "phase": "15_orphan_config_with_blast_radius",
        "description": "Config modules with fan_in<=1 and fan_out>=50 — zombie configs (gap vs check_dead_folder_detector)",
        "category": "orphan_config_with_blast_radius",
        "findings": findings,
    }


# ---------------------------------------------------------------------
# Phase 16 — CI-coverage diff: isolate findings NOT covered by 94 gates
# ---------------------------------------------------------------------

def phase16_uncovered_consolidated(all_phases: dict) -> dict:
    uncovered = []
    for phase_id, payload in all_phases.items():
        cat = payload.get("category", "")
        is_uncovered = cat in UNCOVERED_CATEGORIES
        if is_uncovered:
            findings = payload.get("findings", payload.get("top_files", []))
            uncovered.append({
                "source_phase": phase_id,
                "category": cat,
                "description": payload.get("description", ""),
                "finding_count": len(findings) if isinstance(findings, list) else 0,
                "rationale_for_uncovered": _gap_rationale(cat),
                "ci_gates_closest": _closest_ci_gates(cat),
            })

    return {
        "phase": "16_findings_not_covered_by_ci_gates",
        "description": "Audit findings that have NO existing ADG CI gate enforcing them",
        "ci_gate_count_total": 94,
        "ci_gates_referenced": list(CI_COVERAGE.keys()),
        "uncovered_categories": list(UNCOVERED_CATEGORIES),
        "uncovered_summary": uncovered,
    }


def _gap_rationale(cat: str) -> str:
    rationales = {
        "ssot_duplicate_symbol_name": "No CI gate compares symbol short-names across files/layers; only structural duplication is checked.",
        "ssot_cross_layer_type_redefinition": "No CI gate enforces type SSOT — only L2->L0 layer skip is gated.",
        "untriaged_violation_aging": "No SLA on violations.disposition='untriaged'; ratchet gates measure totals, not aging.",
        "observability_blind_spot_high_fanin": "check_trace_stub_modules detects stubs; no gate detects missing-trace on top-fan-in modules.",
        "hardcoded_external_service_literal": "check_hardcoded_exclusions covers exclusion lists only; doesn't enforce literal SSOT for API versions/IDs.",
        "provider_egress_concentration": "No CI gate ranks per-module external SDK call density.",
        "mixed_callee_layer_dispatcher": "check_layer_skip checks single edges; no aggregate-pattern detection for >=4-layer dispatchers.",
        "cyclic_active_cluster": "check_graph_island finds disconnected components; doesn't flag 2-cycles between living modules.",
        "env_var_outside_config_layer": "check_config_references covers known config refs; doesn't enforce env-var location policy.",
        "orphan_config_with_blast_radius": "check_dead_folder_detector flags folders; this targets specific orphan config modules with high egress.",
    }
    return rationales.get(cat, "No CI gate currently covers this finding category.")


def _closest_ci_gates(cat: str) -> list:
    """Identify the closest existing CI gates to each uncovered category for context."""
    nearby = {
        "ssot_duplicate_symbol_name": ["check_role_dedup", "check_severity_band_ssot"],
        "ssot_cross_layer_type_redefinition": ["check_layer_skip", "check_structure_policy"],
        "untriaged_violation_aging": ["check_baseline_staleness", "check_ledger_freshness"],
        "observability_blind_spot_high_fanin": ["check_trace_stub_modules", "check_w6_trace_theater_kpi", "check_runtime_adg_coverage"],
        "hardcoded_external_service_literal": ["check_hardcoded_exclusions", "check_config_references"],
        "provider_egress_concentration": ["check_w5_missing_adapter", "check_w5_untyped_seam"],
        "mixed_callee_layer_dispatcher": ["check_layer_skip", "check_graph_layer_evidence"],
        "cyclic_active_cluster": ["check_graph_island", "check_graph_reach"],
        "env_var_outside_config_layer": ["check_config_references"],
        "orphan_config_with_blast_radius": ["check_dead_folder_detector", "check_w6_new_orphans_delta"],
    }
    return nearby.get(cat, [])


# ---------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------

def main() -> None:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    cur = con.cursor()

    all_outputs = {}

    print("Phase 1: SSOT duplicate symbol names ...", flush=True)
    p1 = phase1_ssot_duplicate_symbol_names()
    all_outputs["1"] = p1
    (ART / "audit_phase1_ssot_dup_symbols.json").write_text(json.dumps(p1, indent=2, default=str), encoding="utf-8")

    print("Phase 2: Cross-layer type redefinition ...", flush=True)
    p2 = phase2_cross_layer_type_redefinition()
    all_outputs["2"] = p2
    (ART / "audit_phase2_cross_layer_types.json").write_text(json.dumps(p2, indent=2, default=str), encoding="utf-8")

    print("Phase 8: Untriaged violation aging ...", flush=True)
    p8 = phase8_untriaged_aging(cur)
    all_outputs["8"] = p8
    (ART / "audit_phase8_untriaged_aging.json").write_text(json.dumps(p8, indent=2, default=str), encoding="utf-8")

    print("Phase 9: Observability blind spots ...", flush=True)
    p9 = phase9_observability_blind_spots(cur)
    all_outputs["9"] = p9
    (ART / "audit_phase9_observability_blind_spots.json").write_text(json.dumps(p9, indent=2, default=str), encoding="utf-8")

    print("Phase 10: Hardcoded external service literals ...", flush=True)
    p10 = phase10_hardcoded_external_literals(cur)
    all_outputs["10"] = p10
    (ART / "audit_phase10_hardcoded_external.json").write_text(json.dumps(p10, indent=2, default=str), encoding="utf-8")

    print("Phase 11: Provider egress concentration ...", flush=True)
    p11 = phase11_provider_egress(cur)
    all_outputs["11"] = p11
    (ART / "audit_phase11_provider_egress.json").write_text(json.dumps(p11, indent=2, default=str), encoding="utf-8")

    print("Phase 12: Mixed-callee-layer dispatchers ...", flush=True)
    p12 = phase12_mixed_callee_layers(cur)
    all_outputs["12"] = p12
    (ART / "audit_phase12_mixed_callee_layers.json").write_text(json.dumps(p12, indent=2, default=str), encoding="utf-8")

    print("Phase 13: Cyclic active clusters ...", flush=True)
    p13 = phase13_cyclic_clusters(cur)
    all_outputs["13"] = p13
    (ART / "audit_phase13_cyclic_clusters.json").write_text(json.dumps(p13, indent=2, default=str), encoding="utf-8")

    print("Phase 14: Env var outside config layer ...", flush=True)
    p14 = phase14_env_var_outside_config(cur)
    all_outputs["14"] = p14
    (ART / "audit_phase14_env_var.json").write_text(json.dumps(p14, indent=2, default=str), encoding="utf-8")

    print("Phase 15: Orphan config with blast radius ...", flush=True)
    p15 = phase15_orphan_config_blast(cur)
    all_outputs["15"] = p15
    (ART / "audit_phase15_orphan_config.json").write_text(json.dumps(p15, indent=2, default=str), encoding="utf-8")

    print("Phase 16: CI-coverage diff (uncovered findings) ...", flush=True)
    p16 = phase16_uncovered_consolidated(all_outputs)
    (ART / "audit_phase16_uncovered_by_ci.json").write_text(json.dumps(p16, indent=2, default=str), encoding="utf-8")

    con.close()

    # Summary
    print()
    print("=== PHASE OUTPUTS ===")
    for pid, payload in all_outputs.items():
        cnt = len(payload.get("findings", payload.get("top_files", [])))
        cat = payload.get("category", "?")
        print(f"  Phase {pid:>2s}: {cnt:>4d} findings — {cat}")
    print(f"  Phase 16: {len(p16['uncovered_summary'])} uncovered categories (gap vs 94 CI gates)")


if __name__ == "__main__":
    main()
