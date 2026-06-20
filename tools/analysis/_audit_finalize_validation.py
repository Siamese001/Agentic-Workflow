"""Generate validated final report combining Phase 16 categories with cross-check verdicts."""
import json
from pathlib import Path

ART = Path(r"artifacts")

# Validated counts derived from _audit_validate_uncovered.py + _validate_p1_p2.py
validated = {
    "1_ssot_duplicate_symbol_name": {
        "raw_count": 100,
        "validated_count": 97,
        "validation_method": "filter layer_count >= 2",
        "false_positive_rate": "3%",
        "verdict": "CONFIRMED REAL — high signal",
        "top_examples": [
            "BATCH_SIZE / BUFFER_SIZE / THRESHOLD / MAX_RETRIES — each defined in 4 layers (L0,L5,L_APP,L_SHARED) across 11-16 files",
            "ExecutionContext — defined in 5 layers (L2,L3,L4,L6,L_OPS)",
            "main — entry function name in 5 layers (cosmetic, low priority)",
        ],
        "actionable_priority": "P1",
        "remediation_pattern": "Centralize magic constants to agentic_core/L0_routing/config/path_constants.py + delete duplicates",
    },
    "2_ssot_cross_layer_type_redefinition": {
        "raw_count": 100,
        "validated_count": 100,
        "validation_method": "all entries have layer_count >= 2 by query construction",
        "false_positive_rate": "0%",
        "verdict": "CONFIRMED REAL — overlaps heavily with Phase 1",
        "top_examples": [
            "canonical_json — 3 layers (L2,L3,L_SL)",
            "ConfigurationError — 3 layers (L0,L_RUNTIME,L_SHARED)",
            "DEFAULT_TIMEOUT / MAX_DEPTH / MAX_FILES — config constants in 3 layers each",
        ],
        "actionable_priority": "P1",
        "remediation_pattern": "Same as Phase 1 — SSOT consolidation",
    },
    "8_untriaged_violation_aging": {
        "raw_count": 5118,
        "validated_count": 5118,
        "validation_method": "direct violations.disposition='untriaged' query",
        "false_positive_rate": "0%",
        "verdict": "CONFIRMED REAL — 100% of violations are untriaged",
        "top_examples": [
            "antipattern/LOW: 5110 (1694 files, 1429 evidence kinds)",
            "SC-1/P0: 3 (vllm types L2->L0)",
            "antipattern/HIGH: 3 + CRITICAL: 1 + MEDIUM: 1",
        ],
        "actionable_priority": "P3 (process gap, not code defect)",
        "remediation_pattern": "Add CI gate enforcing aging SLA: any violation older than N days must be dispositioned",
    },
    "9_observability_blind_spot_high_fanin": {
        "raw_count": 17,
        "validated_count": 5,
        "validation_method": "broaden trace patterns to include logger/metric/audit/observ/otel/span/emit + L6",
        "false_positive_rate": "70% (12 had hidden trace edges via broader patterns)",
        "verdict": "PARTIALLY CONFIRMED — narrower set is real",
        "true_blind_modules": [
            "agentic_core/L2_execution/_agentic_core_smoke.py (fan_in=118)",
            "agentic_core/L5_safety/config/structure_blueprint/ssot.py (fan_in=80)",
            "agentic_core/L0_routing/config/model_registry.py (fan_in=56)",
            "agentic_core/L5_safety/adapters/human_approval_adapter.py (fan_in=50)",
        ],
        "actionable_priority": "P1 — `human_approval_adapter.py` is L5 safety with no observability — high risk",
        "remediation_pattern": "Add OTel span emission to top 5 truly-blind modules (4 listed + 1 more)",
    },
    "10_hardcoded_external_service_literal": {
        "raw_count": 21,
        "validated_count": 21,
        "validation_method": "direct evidence-pattern match in violations table",
        "false_positive_rate": "0%",
        "verdict": "CONFIRMED REAL — all 21 are NOTION literals in docs/archive/windsurf/legacy-tree/governance_scripts/ (archived from .codex/governance/scripts/_legacy_windsurf/)",
        "breakdown": {
            "NOTION_API_VERSION (literal '2025-09-03')": 10,
            "NOTION_BASE (literal URL)": 3,
            "WAVE_PHASE_DATA_SOURCE_ID": 3,
            "_DATA_SOURCE_ID variants": 3,
            "_PAGE_ID variants": 2,
        },
        "actionable_priority": "P2",
        "remediation_pattern": "Already remediated: _legacy_windsurf/ archived to docs/archive/windsurf/legacy-tree/governance_scripts/ (2026-06-08)",
    },
    "11_provider_egress_concentration": {
        "raw_count": 78,
        "validated_count": 78,
        "validation_method": "raw counts only (no separate validator)",
        "false_positive_rate": "unknown",
        "verdict": "TENTATIVE — needs scoping cut: most are __init__.py re-exports",
        "true_egress_modules": [
            "claude_judge.py (L_SHARED, egress=9)",
            "openai_judge.py (L_SHARED, egress=7)",
            "*_judge.py / vllm_*.py / orchestrator modules",
        ],
        "actionable_priority": "P3 — informational, not necessarily a defect",
        "remediation_pattern": "If concentration is intentional (adapter pattern), add seam-test coverage. If unintentional, route through L_SHARED gateway.",
    },
    "12_mixed_callee_layer_dispatcher": {
        "raw_count": 84,
        "validated_count": 10,
        "validation_method": "filter to >=3 distinct MAINLINE callee layers (L0-L5), exclude self-layer",
        "false_positive_rate": "88% (74 dispatched mostly to utility layers L_SHARED/L_RUNTIME/L_TOOLS — legitimate)",
        "verdict": "CONFIRMED REAL — 10 cross-mainline dispatchers",
        "top_examples": [
            "agentic_core/L5_safety/utils/location_healer_util.py — crosses L0,L2,L3,L4 (4 mainline layers)",
            "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py — crosses L0,L1,L3,L5",
            "agentic_core/L5_safety/reasoning/SystemArchitectAgent.py — crosses L0,L2,L4",
            "agentic_core/L5_safety/reasoning/CodeHealerAgent.py — crosses L0,L2,L3",
            "agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py — crosses L0,L2,L4",
            "agentic_core/L3_orchestration/enforcement/mission_runner.py — crosses L0,L2,L5",
        ],
        "actionable_priority": "P1",
        "remediation_pattern": "Each cross-mainline dispatcher should route through composition_root or a documented seam — not direct imports",
    },
    "13_cyclic_active_cluster": {
        "raw_count": 0,
        "validated_count": 0,
        "validation_method": "module-level 2-cycles + symbol-level call cycles",
        "false_positive_rate": "N/A",
        "verdict": "CONFIRMED CLEAN — no import or call cycles between active modules",
        "actionable_priority": "N/A",
        "remediation_pattern": "Maintain via existing check_graph_island gate",
    },
    "14_env_var_outside_config_layer": {
        "raw_count": 76,
        "validated_count": 50,
        "validation_method": "require explicit edge to os.environ/getenv (not just name pattern)",
        "false_positive_rate": "34%",
        "verdict": "CONFIRMED REAL — 50 modules read env vars outside config/",
        "top_layer_distribution": {
            "L0 (8 modules)": "guardian/runtime mutation guards reading env",
            "L1 (2 modules)": "cognition agents reading env",
            "L2 (15 modules)": "provider adapters, history compressors, key sources reading env",
            "L3-L5": "remaining 25",
        },
        "actionable_priority": "P2",
        "remediation_pattern": "Centralize env reads in agentic_core/L0_routing/config/environment_config.py; modules import the parsed value",
    },
    "15_orphan_config_with_blast_radius": {
        "raw_count": 36,
        "validated_count": 3,
        "validation_method": "exclude configs reachable via flows_to/resolves_callsite/invokes_dynamic/reads_from",
        "false_positive_rate": "92% (33 are dynamic-loader-referenced via importlib pattern)",
        "verdict": "MOSTLY FALSE POSITIVES — only 3 truly orphan",
        "true_orphan_configs": [
            "agentic_core/L5_safety/config/structure_blueprint/semantics.py (fan_out=67)",
            "agentic_core/L2_execution/config/__init__.py (fan_out=62)",
            "agentic_core/L1_cognition/config/__init__.py (fan_out=62)",
        ],
        "actionable_priority": "P3",
        "remediation_pattern": "For 3 true orphans: confirm intentionally-loaded vs dead. For 33 dynamic-loaded: existing pattern is correct, no action needed.",
    },
}

# Composite summary
total_raw = sum(v["raw_count"] for v in validated.values())
total_validated = sum(v["validated_count"] for v in validated.values())

report = {
    "generated_at_utc": "2026-04-25T11:15:00Z",
    "adg_snapshot": "adg_indexed_04252026_0521.sqlite (regenerated 09:25:03Z)",
    "scope": "Validation of 10 uncovered-by-CI categories from Phase 16",
    "headline": {
        "total_raw_findings": total_raw,
        "total_validated_findings": total_validated,
        "false_positive_rate": f"{(1 - total_validated/total_raw) * 100:.1f}%",
        "categories_confirmed_real": sum(1 for v in validated.values() if "CONFIRMED REAL" in v["verdict"]),
        "categories_confirmed_clean": sum(1 for v in validated.values() if "CONFIRMED CLEAN" in v["verdict"]),
        "categories_partial": sum(1 for v in validated.values() if "PARTIALLY" in v["verdict"]),
        "categories_mostly_fp": sum(1 for v in validated.values() if "MOSTLY FALSE" in v["verdict"]),
        "categories_tentative": sum(1 for v in validated.values() if "TENTATIVE" in v["verdict"]),
    },
    "validated_categories": validated,
    "actionable_priority_summary": {
        "P1": [
            "1_ssot_duplicate_symbol_name (97 confirmed)",
            "2_ssot_cross_layer_type_redefinition (100 confirmed)",
            "9_observability_blind_spot_high_fanin (5 confirmed — esp. human_approval_adapter)",
            "12_mixed_callee_layer_dispatcher (10 confirmed)",
        ],
        "P2": [
            "10_hardcoded_external_service_literal (21 NOTION literals)",
            "14_env_var_outside_config_layer (50 confirmed)",
        ],
        "P3": [
            "8_untriaged_violation_aging (5118, process gap)",
            "11_provider_egress_concentration (78, informational)",
            "15_orphan_config_with_blast_radius (3 truly orphan)",
        ],
        "Clean": [
            "13_cyclic_active_cluster (0 cycles — confirmed)",
        ],
    },
    "recommended_new_ci_gates": [
        {
            "gate_name": "check_ssot_magic_constants",
            "scope": "Detect identifiers with same short_name defined in >=3 layers",
            "covers_phases": ["1", "2"],
            "data_source": "ADG nodes table, GROUP BY short_name HAVING layer_count >= 3",
        },
        {
            "gate_name": "check_observability_on_high_fanin",
            "scope": "Modules with fan_in >= 50 must have at least one outgoing edge to L6 or trace/metric/audit symbol",
            "covers_phases": ["9"],
            "data_source": "ADG mv_hotspot_centrality + edges",
        },
        {
            "gate_name": "check_external_service_literal_ssot",
            "scope": "Detect hardcoded API versions, data source IDs, base URLs outside designated SSOT modules",
            "covers_phases": ["10"],
            "data_source": "ADG violations.evidence pattern matching",
        },
        {
            "gate_name": "check_cross_mainline_dispatcher",
            "scope": "No module may dispatch (call/import) to >=3 distinct MAINLINE layers (L0-L5) excluding self",
            "covers_phases": ["12"],
            "data_source": "ADG edges + nodes layer column",
        },
        {
            "gate_name": "check_env_var_in_config_layer",
            "scope": "os.environ/getenv calls allowed only in config/* paths or environment_config.py",
            "covers_phases": ["14"],
            "data_source": "ADG edges to os.environ/os.getenv symbol nodes",
        },
        {
            "gate_name": "check_violation_aging_sla",
            "scope": "Violations with disposition='untriaged' must have dispositioning_due_at within 14 days of first detection",
            "covers_phases": ["8"],
            "data_source": "ADG violations table + first_seen timestamp",
        },
    ],
}

(ART / "audit_validation_final.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("Wrote artifacts/audit_validation_final.json")
print()
print(f"=== HEADLINE ===")
for k, v in report["headline"].items():
    print(f"  {k}: {v}")
print()
print("=== ACTIONABLE PRIORITIES ===")
for prio, items in report["actionable_priority_summary"].items():
    print(f"  {prio}:")
    for item in items:
        print(f"    - {item}")
print()
print(f"=== RECOMMENDED NEW CI GATES ({len(report['recommended_new_ci_gates'])}) ===")
for g in report["recommended_new_ci_gates"]:
    print(f"  {g['gate_name']}")
    print(f"    {g['scope']}")
