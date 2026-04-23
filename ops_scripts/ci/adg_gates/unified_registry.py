"""Unified ADG CI Gate Registry — single SSOT for every ADG-adjacent gate.

H1 consolidation outcome (plan adg-wiring-ci-hardening-7a5d84 Wave H1):
this registry unifies three previously scattered gate planes under a single
(band, enforcement, source) taxonomy anchored in
`agentic_core/adg/severity_bands.py`:

    1. Canonical ADGGateBase gates in `ops_scripts/ci/adg_gates/` (12 gates)
    2. Validation gates in `tools/generate/validation/gates.py` (7 functions)
    3. Residual wiring-CI gates in `ops_scripts/ci/check_*.py` (10 gates,
       post-H1 cleanup — 5 duplicates already deleted)

Band: canonical severity (P0/P1/P2/P3) — never invented; sourced from the
      severity_bands.py SSOT via `severity_to_band` or fixed in code for
      gates that don't map to an ADG antipattern edge.

Enforcement: orthogonal to band — BLOCK / RATCHET / WARN.

Source: which ADG surface the gate reads — SQL / GRAPH / HYBRID / DISK.

The wiring-CI plane's own tier system (B/R/W) is RETIRED in favor of this
single registry. The P1-P5 priority scorer in wiring_ci_regression_markers.py
is RETIRED — priority is now just (band, enforcement).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Band(str, Enum):
    """Canonical severity — matches severity_bands.py SSOT."""

    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class Enforcement(str, Enum):
    BLOCK = "block"  # any violation -> exit 1
    RATCHET = "ratchet"  # count > baseline -> exit 1
    WARN = "warn"  # report only, never exit 1


class Source(str, Enum):
    SQL = "sql"  # reads ADG SQLite only
    GRAPH = "graph"  # reads NetworkX projection (P6b) only
    HYBRID = "hybrid"  # reads both
    DISK = "disk"  # reads working tree (LOC, YAML, waivers)


@dataclass(frozen=True)
class GateSpec:
    gate_id: str
    band: Band
    enforcement: Enforcement
    source: Source
    owner: str  # "adg_gates" | "validation" | "wiring_ci"
    handler: str  # import path or script path
    notes: str = ""
    # H4: in-process class name (WiringGate subclass) inside ``handler`` script.
    # When populated, dispatcher instantiates the class and calls ``.execute()``
    # directly instead of ``subprocess.run(script)``. ``None`` preserves the
    # subprocess fallback for gates not yet migrated.
    gate_class: str | None = None


# -----------------------------------------------------------------------------
# Canonical ADGGateBase gates (plane 1) — already P0-P3 native
# -----------------------------------------------------------------------------
#
# H5 note: for `owner="adg_gates"`, ``handler`` is the dotted module path
# (importable via ``importlib.import_module``) and ``gate_class`` is the
# ADGGateBase subclass within it. The dispatcher's ADGGateBase adapter
# instantiates ``handler.gate_class(sqlite_path=<snapshot>)`` and calls
# ``.run(emit_artifacts=False)`` to avoid file-system side effects in CI.
CANONICAL_GATES: list[GateSpec] = [
    GateSpec(
        "1_critical_path_integrity",
        Band.P0,
        Enforcement.BLOCK,
        Source.SQL,
        "adg_gates",
        "ops_scripts.ci.adg_gates.gate_p0_critical_path",
        gate_class="CriticalPathIntegrityGate",
    ),
    GateSpec(
        "2_authority_boundary",
        Band.P0,
        Enforcement.BLOCK,
        Source.SQL,
        "adg_gates",
        "ops_scripts.ci.adg_gates.gate_p0_authority",
        gate_class="AuthorityBoundaryGate",
    ),
    GateSpec(
        "3_write_sovereignty",
        Band.P0,
        Enforcement.BLOCK,
        Source.SQL,
        "adg_gates",
        "ops_scripts.ci.adg_gates.gate_p0_write_sovereignty",
        notes="Covers UWG bypass — S2_uwg_bypass_ratchet is a RATCHET overlay on the same edges",
        gate_class="WriteSovereigntyGate",
    ),
    GateSpec(
        "4_capability_egress",
        Band.P0,
        Enforcement.BLOCK,
        Source.SQL,
        "adg_gates",
        "ops_scripts.ci.adg_gates.gate_p0_capability_egress",
        gate_class="CapabilityEgressGate",
    ),
    GateSpec(
        "5_text_to_action",
        Band.P0,
        Enforcement.BLOCK,
        Source.SQL,
        "adg_gates",
        "ops_scripts.ci.adg_gates.gate_p0_text_to_action",
        gate_class="TextToActionGate",
    ),
    GateSpec(
        "6_determinism_provenance",
        Band.P0,
        Enforcement.BLOCK,
        Source.SQL,
        "adg_gates",
        "ops_scripts.ci.adg_gates.gate_p0_determinism",
        gate_class="DeterminismProvenanceGate",
    ),
    GateSpec(
        "7_lifecycle_coverage",
        Band.P1,
        Enforcement.RATCHET,
        Source.SQL,
        "adg_gates",
        "ops_scripts.ci.adg_gates.gate_p1_lifecycle",
        gate_class="LifecycleCoverageGate",
    ),
    GateSpec(
        "8_trace_replay_eval",
        Band.P1,
        Enforcement.RATCHET,
        Source.SQL,
        "adg_gates",
        "ops_scripts.ci.adg_gates.gate_p1_trace_replay",
        gate_class="TraceReplayEvalGate",
    ),
    GateSpec(
        "9_executor_theater",
        Band.P0,
        Enforcement.BLOCK,
        Source.HYBRID,
        "adg_gates",
        "ops_scripts.ci.adg_gates.gate_executor_theater",
        notes="Covers trace-theater — E1_trace_stub_module is a RATCHET overlay",
        gate_class="ExecutorTheaterGate",
    ),
    GateSpec(
        "10_infra_wiring",
        Band.P0,
        Enforcement.BLOCK,
        Source.SQL,
        "adg_gates",
        "ops_scripts.ci.adg_gates.gate_infra_wiring",
        gate_class="InfraWiringGate",
    ),
    GateSpec(
        "11_architecture_witness",
        Band.P1,
        Enforcement.BLOCK,
        Source.SQL,
        "adg_gates",
        "ops_scripts.ci.adg_gates.gate_p1_architecture_witness",
        gate_class="ArchitectureWitnessGate",
    ),
    GateSpec(
        "12_prompt_assembly_wiring",
        Band.P1,
        Enforcement.BLOCK,
        Source.SQL,
        "adg_gates",
        "ops_scripts.ci.adg_gates.gate_p1_prompt_wiring",
        notes="Covers specific prompt-assembly paths — J1_canonical_pipeline_wiring generalizes this to any pipeline declared in canonical_pipelines.yaml",
        gate_class="PromptAssemblyWiringGate",
    ),
]

# -----------------------------------------------------------------------------
# Validation gates (plane 2) — the _check_* functions in generate_full_adg flow
# -----------------------------------------------------------------------------
VALIDATION_GATES: list[GateSpec] = [
    GateSpec(
        "v_p0_violations",
        Band.P0,
        Enforcement.BLOCK,
        Source.SQL,
        "validation",
        "validation.gates._check_p0_violations",
    ),
    GateSpec(
        "v_p1_ratchet",
        Band.P1,
        Enforcement.RATCHET,
        Source.SQL,
        "validation",
        "validation.gates._check_p1_ratchet",
    ),
    GateSpec(
        "v_p2_ratchet",
        Band.P2,
        Enforcement.RATCHET,
        Source.SQL,
        "validation",
        "validation.gates._check_p2_ratchet",
    ),
    GateSpec(
        "v_dead_production_imports",
        Band.P1,
        Enforcement.BLOCK,
        Source.SQL,
        "validation",
        "validation.gates._check_dead_production_imports",
        notes="Covers orphan modules — A1_orphan_module_ratchet RETIRED 2026-04-23 as exact duplicate",
    ),
    GateSpec(
        "v_structural_conformance",
        Band.P0,
        Enforcement.BLOCK,
        Source.SQL,
        "validation",
        "validation.gates._check_structural_conformance",
        notes="SC-1 layer gravity+cycles (BLOCK 2026-04-23); SC-5 spine completeness (promoted audit->BLOCK in H2 2026-04-23, 0 current violations); SC-7 grounding contract (promoted disabled->enabled+audit RATCHET in H2 2026-04-23, 0 current violations)",
    ),
    GateSpec(
        "v_agentic_antipatterns",
        Band.P1,
        Enforcement.BLOCK,
        Source.SQL,
        "validation",
        "validation.gates._check_agentic_antipatterns",
        notes="AP-18 prompt-assembly disconnect (BLOCK); AP-14 retrieval without evidence contract (promoted disabled->enabled+audit RATCHET in H2 2026-04-23, 2 current violations surfacing)",
    ),
    GateSpec(
        "v_witness_tier_gates",
        Band.P1,
        Enforcement.BLOCK,
        Source.SQL,
        "validation",
        "validation.gates._check_witness_tier_gates",
    ),
]

# -----------------------------------------------------------------------------
# Residual wiring-CI gates (plane 3) — post-H1 cleanup
#
# Note retired gates (deleted 2026-04-23):
#   A1_orphan_module_ratchet     -> v_dead_production_imports (plane 2)
#   A6_import_cycle              -> v_structural_conformance (SC-1 cycles)
#   L1_layer_gravity             -> v_structural_conformance (SC-1 gravity)
#   S1_global_state_mutation     -> v_p2_ratchet (antipattern.global_state_mutation)
#   S3_exception_swallow         -> v_p1_ratchet + v_p2_ratchet (4 swallow edges)
# -----------------------------------------------------------------------------
WIRING_GATES: list[GateSpec] = [
    GateSpec(
        "J1_canonical_pipeline_wiring",
        Band.P0,
        Enforcement.BLOCK,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_canonical_pipeline_wiring.py",
        notes="Generalizes gate 12 to any pipeline declared in canonical_pipelines.yaml",
        gate_class="CanonicalPipelineWiringGate",
    ),
    GateSpec(
        "G2_seam_test_export_coherence",
        Band.P1,
        Enforcement.BLOCK,
        Source.DISK,
        "wiring_ci",
        "ops_scripts/ci/check_seam_test_export_coherence.py",
        gate_class="SeamTestExportCoherenceGate",
    ),
    GateSpec(
        "E1_trace_stub_module",
        Band.P1,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_trace_stub_modules.py",
        notes="Ratchet overlay on gate 9 ExecutorTheaterGate — finer-grained import-ratio signal",
        gate_class="TraceStubModuleGate",
    ),
    GateSpec(
        "A3_dead_public_symbol_ratchet",
        Band.P2,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_dead_symbols_ratchet.py",
        gate_class="DeadSymbolRatchetGate",
    ),
    GateSpec(
        "L2_lpg_drift_ratchet",
        Band.P0,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_lpg_drift_ratchet.py",
        notes="Finer-grained than SC-1 — specific to L_PG boundary",
        gate_class="LpgDriftRatchetGate",
    ),
    GateSpec(
        "M1_module_loc_ratchet",
        Band.P3,
        Enforcement.RATCHET,
        Source.DISK,
        "wiring_ci",
        "ops_scripts/ci/check_module_loc_ratchet.py",
        gate_class="ModuleLocRatchetGate",
    ),
    GateSpec(
        "D1_layer_doc_binding",
        Band.P3,
        Enforcement.WARN,
        Source.DISK,
        "wiring_ci",
        "ops_scripts/ci/check_layer_doc_binding.py",
        gate_class="LayerDocBindingGate",
    ),
    GateSpec(
        "S2_uwg_bypass_ratchet",
        Band.P0,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_uwg_bypass_ratchet.py",
        notes="Ratchet overlay on gate 3 WriteSovereigntyGate with named allowlist contract",
        gate_class="UwgBypassRatchetGate",
    ),
    GateSpec(
        "S4_unused_imports_ratchet",
        Band.P3,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_unused_imports_ratchet.py",
        gate_class="UnusedImportsRatchetGate",
    ),
    GateSpec(
        "W5_waiver_expiry",
        Band.P0,
        Enforcement.BLOCK,
        Source.DISK,
        "wiring_ci",
        "ops_scripts/ci/check_waiver_expiry.py",
        notes="Governance gate — blocks on any expired wiring-CI waiver",
        gate_class="WaiverExpiryGate",
    ),
    # -- W3 residuals shipped 2026-04-23 -------------------------------------
    GateSpec(
        "B2_layer_skip_ratchet",
        Band.P1,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_layer_skip.py",
        notes="W3.1 — imports edges on L0..L6 that skip >1 layer ordinal. Complements SC-1 (direction) with a distance signal.",
        gate_class="LayerSkipGate",
    ),
    GateSpec(
        "D2_role_duplication_warn",
        Band.P2,
        Enforcement.WARN,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_role_dedup.py",
        notes="W3.4 — role-suffix clusters (_reranker, _retriever, _planner, ...) where any member has fan_in=0. Signature of shadow SSOT reconstruction.",
        gate_class="RoleDedupGate",
    ),
    GateSpec(
        "Q2_cyclomatic_complexity_ratchet",
        Band.P3,
        Enforcement.RATCHET,
        Source.DISK,
        "wiring_ci",
        "ops_scripts/ci/check_cyclomatic_ceiling.py",
        notes="W3.6 — McCabe cyclomatic complexity per function > 15.",
        gate_class="CyclomaticCeilingGate",
    ),
    # -- W4 semantic-edge gates shipped 2026-04-23 ---------------------------
    GateSpec(
        "C1_uwg_bypass_pview",
        Band.P0,
        Enforcement.BLOCK,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_w4_uwg_bypass_pview.py",
        notes="W4.1 — mirrors v_p0_write_bypass_uwg; any row blocks. Distinct from S2 ratchet overlay.",
        gate_class="UwgBypassPViewGate",
    ),
    GateSpec(
        "C2_l5_bypass_pview",
        Band.P0,
        Enforcement.BLOCK,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_w4_l5_bypass.py",
        notes="W4.2 — mirrors mv_gateway_bypass_paths; provider/tool calls that skip L5 gateway.",
        gate_class="L5BypassGate",
    ),
    GateSpec(
        "C3_silent_writes_ratchet",
        Band.P1,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_w4_silent_writes.py",
        notes="W4.3 — writes_to without sibling emits_side_effect on same src_id.",
        gate_class="SilentWritesGate",
    ),
    GateSpec(
        "C4_policy_without_audit_ratchet",
        Band.P1,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_w4_policy_without_audit.py",
        notes="W4.4 — controls_flow without sibling audit emission (emits_side_effect / syncs_l4_telemetry / l6_ingests_l4_trace).",
        gate_class="PolicyWithoutAuditGate",
    ),
    GateSpec(
        "C5_unresolved_callsites_ratchet",
        Band.P2,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_w4_unresolved_callsites.py",
        notes="W4.5 — resolves_callsite edges with NULL dst_id; erodes analysis precision.",
        gate_class="UnresolvedCallsitesGate",
    ),
    GateSpec(
        "I1_exit_disposition_ratchet",
        Band.P1,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_w4_exit_disposition.py",
        notes="W4.6 — mv_exit_disposition_coverage rows with is_terminal_covered=0.",
        gate_class="ExitDispositionGate",
    ),
    GateSpec(
        "I2_replay_surface_gaps_ratchet",
        Band.P2,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_w4_replay_surface_gaps.py",
        notes="W4.7 — mv_replay_surface_gaps rows with gap_flag=1; mutations not consumed by replay surface.",
        gate_class="ReplaySurfaceGapsGate",
    ),
    GateSpec(
        "O_tool_call_parity_ratchet",
        Band.P1,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_w4_tool_call_parity.py",
        notes="W4.8 — Anthropic pattern: tool invocation without observability receipt.",
        gate_class="ToolCallParityGate",
    ),
    GateSpec(
        "N_guardrail_separation_ratchet",
        Band.P1,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_w4_guardrail_separation.py",
        notes="W4.9 — Anthropic evaluator-optimizer pattern: L5 guardrail and L3 core-response sharing writes_to target.",
        gate_class="GuardrailSeparationGate",
    ),
    # -- W5 dataflow gates shipped 2026-04-23 (L CVE deferred per DEFERRED_SCOPE)
    GateSpec(
        "M_taint_actionable_ratchet",
        Band.P1,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_w5_taint_actionable.py",
        notes="W5.1 — OpenAI Agent-Builder Safety: actionable surfaces without output schema.",
        gate_class="TaintActionableGate",
    ),
    GateSpec(
        "P_structured_output_ratchet",
        Band.P1,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_w5_structured_output.py",
        notes="W5.2 — OpenAI structured-field extraction boundary: generates_prompt at scale without schema.",
        gate_class="StructuredOutputGate",
    ),
    GateSpec(
        "F1_untyped_seam_ratchet",
        Band.P2,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_w5_untyped_seam.py",
        notes="W5.4 — Cross-layer imports where target has empty type_surface.",
        gate_class="UntypedSeamGate",
    ),
    GateSpec(
        "F2_broken_contract_ratchet",
        Band.P2,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_w5_broken_contract.py",
        notes="W5.5 — Import target publishes 0 exports edges; contract drift indicator.",
        gate_class="BrokenContractGate",
    ),
    GateSpec(
        "F3_missing_adapter_warn",
        Band.P3,
        Enforcement.WARN,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_w5_missing_adapter.py",
        notes="W5.6 — Protocol/ABC/Interface class with zero implements edges.",
        gate_class="MissingAdapterGate",
    ),
    # W5.3 Gate L (CVE propagation) — DEFERRED: needs OSV/deps.dev external client.
    # -- W6 temporal + KPI gates shipped 2026-04-23 --------------------------
    GateSpec(
        "H1_new_orphans_delta_ratchet",
        Band.P1,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_w6_new_orphans_delta.py",
        notes="W6.1 — modules with fan_in=0 in current snapshot but not in prior snapshot.",
        gate_class="NewOrphansDeltaGate",
    ),
    GateSpec(
        "H2_fanin_collapse_ratchet",
        Band.P1,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_w6_fanin_collapse.py",
        notes="W6.2 — top-50 centrality hotspots with >30% fan_in drop vs prior snapshot.",
        gate_class="FaninCollapseGate",
    ),
    GateSpec(
        "H4_mv_staleness_ratchet",
        Band.P2,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_w6_mv_staleness.py",
        notes="W6.6 — total edges count delta >5% between current and prior snapshot.",
        gate_class="MvStalenessGate",
    ),
    GateSpec(
        "K1_churn_complexity_kpi",
        Band.P3,
        Enforcement.WARN,
        Source.DISK,
        "wiring_ci",
        "ops_scripts/ci/check_w6_churn_complexity_kpi.py",
        notes="W6.3 KPI — CodeScene formula churn × complexity per file; K-tier, writes kpi_churn_complexity.jsonl.",
        gate_class="ChurnComplexityKpiGate",
    ),
    GateSpec(
        "E3_trace_theater_kpi",
        Band.P3,
        Enforcement.WARN,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_w6_trace_theater_kpi.py",
        notes="W6.4 KPI — emit-symbol count / production imports per layer; K-tier, writes kpi_trace_theater.jsonl.",
        gate_class="TraceTheaterKpiGate",
    ),
    GateSpec(
        "H3_ap_velocity_kpi",
        Band.P3,
        Enforcement.WARN,
        Source.HYBRID,
        "wiring_ci",
        "ops_scripts/ci/check_w6_ap_velocity_kpi.py",
        notes="W6.5 KPI — antipattern edge count per 1k production LOC; K-tier, writes kpi_ap_velocity.jsonl.",
        gate_class="ApVelocityKpiGate",
    ),
    # -- Graph-native gates (added in H2, 2026-04-23) -----------------------
    GateSpec(
        "G_REACH_l0_reachability",
        Band.P0,
        Enforcement.RATCHET,
        Source.GRAPH,
        "wiring_ci",
        "ops_scripts/ci/check_graph_reach.py",
        notes="H2 graph-native. NetworkX descendants-from-L0 over 'imports' edges. 2nd independent signal for C0-class wiring gaps. Baseline 1993 seeded 2026-04-23; flip to BLOCK after C0 wiring fix.",
        gate_class="GraphReachGate",
    ),
    GateSpec(
        "G_ISLAND_connected_components",
        Band.P1,
        Enforcement.RATCHET,
        Source.GRAPH,
        "wiring_ci",
        "ops_scripts/ci/check_graph_island.py",
        notes="H2 graph-native. Non-giant connected components via nx.connected_components on undirected 'imports' projection. Baseline 0 seeded 2026-04-23.",
        gate_class="GraphIslandGate",
    ),
    GateSpec(
        "G_WATCHLIST_DELTA_hotspot_regressions",
        Band.P1,
        Enforcement.RATCHET,
        Source.GRAPH,
        "wiring_ci",
        "ops_scripts/ci/check_graph_watchlist_delta.py",
        notes="H2 graph-native. Wraps ADGGraphWatchlistBuilder regression classification; promotes previously-passive intelligence to exit-code gate. Baseline 0 seeded 2026-04-23.",
        gate_class="GraphWatchlistDeltaGate",
    ),
]

# -----------------------------------------------------------------------------
# Unified SSOT — iterate for run-all / run-by-band / run-by-enforcement
# -----------------------------------------------------------------------------
ALL_GATES: list[GateSpec] = CANONICAL_GATES + VALIDATION_GATES + WIRING_GATES


def by_band(band: Band) -> list[GateSpec]:
    return [g for g in ALL_GATES if g.band == band]


def by_enforcement(enforcement: Enforcement) -> list[GateSpec]:
    return [g for g in ALL_GATES if g.enforcement == enforcement]


def by_owner(owner: str) -> list[GateSpec]:
    return [g for g in ALL_GATES if g.owner == owner]


def get_spec(gate_id: str) -> GateSpec | None:
    for g in ALL_GATES:
        if g.gate_id == gate_id:
            return g
    return None


# Count summary for H1 validation
def summary_counts() -> dict[str, int]:
    return {
        "total_gates": len(ALL_GATES),
        "canonical_plane": len(CANONICAL_GATES),
        "validation_plane": len(VALIDATION_GATES),
        "wiring_plane_residual": len(WIRING_GATES),
        "band_P0": len(by_band(Band.P0)),
        "band_P1": len(by_band(Band.P1)),
        "band_P2": len(by_band(Band.P2)),
        "band_P3": len(by_band(Band.P3)),
        "enforcement_block": len(by_enforcement(Enforcement.BLOCK)),
        "enforcement_ratchet": len(by_enforcement(Enforcement.RATCHET)),
        "enforcement_warn": len(by_enforcement(Enforcement.WARN)),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(summary_counts(), indent=2))
