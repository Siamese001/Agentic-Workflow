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


# -----------------------------------------------------------------------------
# Canonical ADGGateBase gates (plane 1) — already P0-P3 native
# -----------------------------------------------------------------------------
CANONICAL_GATES: list[GateSpec] = [
    GateSpec(
        "1_critical_path_integrity",
        Band.P0,
        Enforcement.BLOCK,
        Source.SQL,
        "adg_gates",
        "CriticalPathIntegrityGate",
    ),
    GateSpec(
        "2_authority_boundary", Band.P0, Enforcement.BLOCK, Source.SQL, "adg_gates", "AuthorityBoundaryGate"
    ),
    GateSpec(
        "3_write_sovereignty",
        Band.P0,
        Enforcement.BLOCK,
        Source.SQL,
        "adg_gates",
        "WriteSovereigntyGate",
        notes="Covers UWG bypass — S2_uwg_bypass_ratchet is a RATCHET overlay on the same edges",
    ),
    GateSpec(
        "4_capability_egress", Band.P0, Enforcement.BLOCK, Source.SQL, "adg_gates", "CapabilityEgressGate"
    ),
    GateSpec("5_text_to_action", Band.P0, Enforcement.BLOCK, Source.SQL, "adg_gates", "TextToActionGate"),
    GateSpec(
        "6_determinism_provenance",
        Band.P0,
        Enforcement.BLOCK,
        Source.SQL,
        "adg_gates",
        "DeterminismProvenanceGate",
    ),
    GateSpec(
        "7_lifecycle_coverage", Band.P1, Enforcement.RATCHET, Source.SQL, "adg_gates", "LifecycleCoverageGate"
    ),
    GateSpec(
        "8_trace_replay_eval", Band.P1, Enforcement.RATCHET, Source.SQL, "adg_gates", "TraceReplayEvalGate"
    ),
    GateSpec(
        "9_executor_theater",
        Band.P0,
        Enforcement.BLOCK,
        Source.HYBRID,
        "adg_gates",
        "ExecutorTheaterGate",
        notes="Covers trace-theater — E1_trace_stub_module is a RATCHET overlay",
    ),
    GateSpec("10_infra_wiring", Band.P0, Enforcement.BLOCK, Source.SQL, "adg_gates", "InfraWiringGate"),
    GateSpec(
        "11_architecture_witness",
        Band.P1,
        Enforcement.BLOCK,
        Source.SQL,
        "adg_gates",
        "ArchitectureWitnessGate",
    ),
    GateSpec(
        "12_prompt_assembly_wiring",
        Band.P1,
        Enforcement.BLOCK,
        Source.SQL,
        "adg_gates",
        "PromptAssemblyWiringGate",
        notes="Covers specific prompt-assembly paths — J1_canonical_pipeline_wiring generalizes this to any pipeline declared in canonical_pipelines.yaml",
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
        notes="SC-1 covers layer gravity + cycles; SC-5 spine completeness; SC-7 grounding contract",
    ),
    GateSpec(
        "v_agentic_antipatterns",
        Band.P1,
        Enforcement.BLOCK,
        Source.SQL,
        "validation",
        "validation.gates._check_agentic_antipatterns",
        notes="AP-18 prompt-assembly disconnect (enabled); AP-14 retrieval without evidence contract (disabled; queued for H2)",
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
    ),
    GateSpec(
        "G2_seam_test_export_coherence",
        Band.P1,
        Enforcement.BLOCK,
        Source.DISK,
        "wiring_ci",
        "ops_scripts/ci/check_seam_test_export_coherence.py",
    ),
    GateSpec(
        "E1_trace_stub_module",
        Band.P1,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_trace_stub_modules.py",
        notes="Ratchet overlay on gate 9 ExecutorTheaterGate — finer-grained import-ratio signal",
    ),
    GateSpec(
        "A3_dead_public_symbol_ratchet",
        Band.P2,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_dead_symbols_ratchet.py",
    ),
    GateSpec(
        "L2_lpg_drift_ratchet",
        Band.P0,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_lpg_drift_ratchet.py",
        notes="Finer-grained than SC-1 — specific to L_PG boundary",
    ),
    GateSpec(
        "M1_module_loc_ratchet",
        Band.P3,
        Enforcement.RATCHET,
        Source.DISK,
        "wiring_ci",
        "ops_scripts/ci/check_module_loc_ratchet.py",
    ),
    GateSpec(
        "D1_layer_doc_binding",
        Band.P3,
        Enforcement.WARN,
        Source.DISK,
        "wiring_ci",
        "ops_scripts/ci/check_layer_doc_binding.py",
    ),
    GateSpec(
        "S2_uwg_bypass_ratchet",
        Band.P0,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_uwg_bypass_ratchet.py",
        notes="Ratchet overlay on gate 3 WriteSovereigntyGate with named allowlist contract",
    ),
    GateSpec(
        "S4_unused_imports_ratchet",
        Band.P3,
        Enforcement.RATCHET,
        Source.SQL,
        "wiring_ci",
        "ops_scripts/ci/check_unused_imports_ratchet.py",
    ),
    GateSpec(
        "W5_waiver_expiry",
        Band.P0,
        Enforcement.BLOCK,
        Source.DISK,
        "wiring_ci",
        "ops_scripts/ci/check_waiver_expiry.py",
        notes="Governance gate — blocks on any expired wiring-CI waiver",
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
