"""ADG CI Gate SSOT Catalog.

Single source of truth for all ADG CI gates. Every gate that participates in
the P0-P3 enforcement pipeline MUST have an entry here.

Catalog fields per gate (all required — validated at module load time):
    gate_id     — unique gate identifier (e.g. G-P0-WRITE)
    file        — Python module implementing the gate (relative to repo root)
    cls         — class name (or None for legacy script gates)
    severity    — P0, P1, P2, or P3
    gate_class  — structural_conformance | agentic_antipattern | hygiene
    policy      — ExecutionPolicy with all 6 required fields

Classification decisions from HITL approval (design package, 2026):
    H1: adg_p1_defect_gate.py reclassified P0, renamed adg_critical_defect_gate.py
    H2: Preflight scope = text_to_action + write_sovereignty only
    H3: M1-M6 migrated to ADGGateBase subclasses (target state; M1-M6 files TBD Phase 03)
"""

from __future__ import annotations

import sys
from pathlib import Path


def _bootstrap_repo_root() -> Path:
    repo_root = Path(__file__).resolve().parents[3]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    return repo_root


_REPO_ROOT = _bootstrap_repo_root()

from dataclasses import dataclass, field
from typing import Any

from ops_scripts.ci.adg_gates.gate_policy import ExecutionPolicy


# ---------------------------------------------------------------------------
# Catalog entry
# ---------------------------------------------------------------------------


@dataclass
class GateCatalogEntry:
    """SSOT record for a single gate family."""

    gate_id: str
    file: str
    cls: str | None
    severity: str
    gate_class: str
    policy: ExecutionPolicy
    notes: str = ""

    def validate(self) -> list[str]:
        """Return list of validation errors. Empty = valid."""
        errors: list[str] = []
        if not self.gate_id:
            errors.append("gate_id is required")
        if not self.file:
            errors.append("file is required")
        if self.severity not in ("P0", "P1", "P2", "P3"):
            errors.append(f"severity={self.severity!r} must be P0/P1/P2/P3")
        if self.gate_class not in ("structural_conformance", "agentic_antipattern", "hygiene"):
            errors.append(
                f"gate_class={self.gate_class!r} must be structural_conformance | "
                "agentic_antipattern | hygiene"
            )
        errors.extend(self.policy.validate())
        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "file": self.file,
            "cls": self.cls,
            "severity": self.severity,
            "gate_class": self.gate_class,
            "policy": self.policy.to_dict(),
            "notes": self.notes,
        }


# ---------------------------------------------------------------------------
# Catalog definition
# ---------------------------------------------------------------------------

GATE_CATALOG: list[GateCatalogEntry] = [
    # -----------------------------------------------------------------------
    # P0 — structural_conformance gates (adg_gates/ subpackage)
    # -----------------------------------------------------------------------
    GateCatalogEntry(
        gate_id="G-P0-WRITE",
        file="ops_scripts/ci/adg_gates/gate_p0_write_sovereignty.py",
        cls="WriteSovereigntyGate",
        severity="P0",
        gate_class="agentic_antipattern",
        policy=ExecutionPolicy(
            stage="preflight+full",
            repairability="manual_only",
            gate_action="halt",
            artifact_policy="minimal_failure_artifact",
            signal_source="sqlite_mv_ci",
            evidence_tier="truth",
        ),
        notes="H2: preflight-capable. Blocks direct writes bypassing UWG.",
    ),
    GateCatalogEntry(
        gate_id="G-P0-TTA",
        file="ops_scripts/ci/adg_gates/gate_p0_text_to_action.py",
        cls="TextToActionGate",
        severity="P0",
        gate_class="agentic_antipattern",
        policy=ExecutionPolicy(
            stage="preflight+full",
            repairability="suggest_only",
            gate_action="halt",
            artifact_policy="minimal_failure_artifact",
            signal_source="sqlite_mv_ci",
            evidence_tier="truth",
        ),
        notes="H2: preflight-capable. Blocks unvalidated text-to-action paths.",
    ),
    GateCatalogEntry(
        gate_id="G-P0-AUTH",
        file="ops_scripts/ci/adg_gates/gate_p0_authority.py",
        cls="AuthorityBoundaryGate",
        severity="P0",
        gate_class="structural_conformance",
        policy=ExecutionPolicy(
            stage="full",
            repairability="manual_only",
            gate_action="halt",
            artifact_policy="full_adg_report",
            signal_source="sqlite_mv_ci",
            evidence_tier="truth",
        ),
        notes="Full-only. Blocks illegal L0/L1/L6/L2/UWG boundary crossings.",
    ),
    GateCatalogEntry(
        gate_id="G-P0-CAP",
        file="ops_scripts/ci/adg_gates/gate_p0_capability_egress.py",
        cls="CapabilityEgressGate",
        severity="P0",
        gate_class="structural_conformance",
        policy=ExecutionPolicy(
            stage="full",
            repairability="manual_only",
            gate_action="halt",
            artifact_policy="full_adg_report",
            signal_source="sqlite_mv_ci",
            evidence_tier="truth",
        ),
        notes="Full-only. Blocks capability egress violations.",
    ),
    GateCatalogEntry(
        gate_id="G-P0-CRIT",
        file="ops_scripts/ci/adg_gates/gate_p0_critical_path.py",
        cls="CriticalPathGate",
        severity="P0",
        gate_class="structural_conformance",
        policy=ExecutionPolicy(
            stage="full",
            repairability="manual_only",
            gate_action="halt",
            artifact_policy="full_adg_report",
            signal_source="sqlite_mv_ci",
            evidence_tier="truth",
        ),
        notes="Full-only. Blocks critical path integrity failures.",
    ),
    GateCatalogEntry(
        gate_id="G-P0-DET",
        file="ops_scripts/ci/adg_gates/gate_p0_determinism.py",
        cls="DeterminismGate",
        severity="P0",
        gate_class="structural_conformance",
        policy=ExecutionPolicy(
            stage="full",
            repairability="suggest_only",
            gate_action="halt",
            artifact_policy="full_adg_report",
            signal_source="sqlite_mv_ci",
            evidence_tier="truth",
        ),
        notes="Full-only. Blocks determinism violations (wall-clock, unseeded RNG).",
    ),
    # -----------------------------------------------------------------------
    # P0 — legacy script gate reclassified from P1 (HITL H1)
    # -----------------------------------------------------------------------
    GateCatalogEntry(
        gate_id="G-P0-CRIT-DEF",
        file="ops_scripts/ci/adg_critical_defect_gate.py",
        cls=None,
        severity="P0",
        gate_class="structural_conformance",
        policy=ExecutionPolicy(
            stage="full",
            repairability="manual_only",
            gate_action="halt",
            artifact_policy="full_adg_report",
            signal_source="canonical_policy",
            evidence_tier="truth",
        ),
        notes="H1: reclassified P0, renamed from adg_p1_defect_gate.py. "
        "Queries SeverityLevel.CRITICAL from ADG SQLite.",
    ),
    # -----------------------------------------------------------------------
    # P0 — layer violation (legacy standalone gate)
    # -----------------------------------------------------------------------
    GateCatalogEntry(
        gate_id="G-P0-LAYER",
        file="ops_scripts/ci/adg_layer_violation_gate.py",
        cls=None,
        severity="P0",
        gate_class="structural_conformance",
        policy=ExecutionPolicy(
            stage="full",
            repairability="manual_only",
            gate_action="halt",
            artifact_policy="full_adg_report",
            signal_source="canonical_policy",
            evidence_tier="truth",
        ),
        notes="Legacy standalone gate. Blocks ADG layer boundary violations.",
    ),
    # -----------------------------------------------------------------------
    # P0 — GraphDB projection gates (derived_explainer, not canonical truth)
    # -----------------------------------------------------------------------
    GateCatalogEntry(
        gate_id="G-GDB-P0",
        file="ops_scripts/ci/graphdb_p0_gate.py",
        cls=None,
        severity="P0",
        gate_class="hygiene",
        policy=ExecutionPolicy(
            stage="full",
            repairability="suggest_only",
            gate_action="halt",
            artifact_policy="parity_failure_artifact",
            signal_source="graphdb_ci",
            evidence_tier="derived_explainer",
        ),
        notes="GraphDB projection parity + integrity gates (P0-1..P0-6). "
        "Derived explainer only — not canonical CI truth.",
    ),
    # -----------------------------------------------------------------------
    # P1 — lifecycle + trace replay (adg_gates/ subpackage)
    # -----------------------------------------------------------------------
    GateCatalogEntry(
        gate_id="G-P1-LIFE",
        file="ops_scripts/ci/adg_gates/gate_p1_lifecycle.py",
        cls="LifecycleGate",
        severity="P1",
        gate_class="structural_conformance",
        policy=ExecutionPolicy(
            stage="full",
            repairability="suggest_only",
            gate_action="ratchet",
            artifact_policy="full_adg_report",
            signal_source="sqlite_mv_ci",
            evidence_tier="truth",
        ),
        notes="Path-aware ratchet. Blocks lifecycle contract violations.",
    ),
    GateCatalogEntry(
        gate_id="G-P1-TRACE",
        file="ops_scripts/ci/adg_gates/gate_p1_trace_replay.py",
        cls="TraceReplayGate",
        severity="P1",
        gate_class="structural_conformance",
        policy=ExecutionPolicy(
            stage="full",
            repairability="suggest_only",
            gate_action="ratchet",
            artifact_policy="full_adg_report",
            signal_source="sqlite_mv_ci",
            evidence_tier="truth",
        ),
        notes="Path-aware ratchet. Blocks trace/replay contract violations.",
    ),
    GateCatalogEntry(
        gate_id="G-P1-PROMPT-WIRING",
        file="ops_scripts/ci/adg_gates/gate_p1_prompt_wiring.py",
        cls="PromptAssemblyWiringGate",
        severity="P1",
        gate_class="structural_conformance",
        policy=ExecutionPolicy(
            stage="full",
            repairability="manual_only",
            gate_action="halt",
            artifact_policy="full_adg_report",
            signal_source="sqlite_mv_ci",
            evidence_tier="truth",
        ),
        notes=(
            "Blocks when prompt-assembly subsystem (dispatcher/bridge/contracts) "
            "is test-covered but has zero live runtime callers. "
            "Reads mv_prompt_assembly_wiring_gaps; falls back to inline SQL. "
            "Exact condition: gap_type='disconnected' AND test_callers>0."
        ),
    ),
    # -----------------------------------------------------------------------
    # P1 — M1-M6 wave0 ratchet gates (migrating to ADGGateBase — Phase 03)
    # Entries use target gate_ids; legacy _adg_ci_gates.py is the shim until
    # individual gate_m*.py files are created.
    # -----------------------------------------------------------------------
    GateCatalogEntry(
        gate_id="G-M1-DET",
        file="ops_scripts/ci/adg_gates/gate_m1_determinism.py",
        cls="M1DeterminismGate",
        severity="P1",
        gate_class="hygiene",
        policy=ExecutionPolicy(
            stage="full",
            repairability="suggest_only",
            gate_action="ratchet",
            artifact_policy="full_adg_report",
            signal_source="canonical_policy",
            evidence_tier="truth",
        ),
        notes="H3: migrating from _adg_ci_gates.py M1. "
        "Blocks wall_clock delta > 0 without determinism_digest.",
    ),
    GateCatalogEntry(
        gate_id="G-M2-DISPATCH",
        file="ops_scripts/ci/adg_gates/gate_m2_dispatch_visibility.py",
        cls="M2DispatchVisibilityGate",
        severity="P1",
        gate_class="hygiene",
        policy=ExecutionPolicy(
            stage="full",
            repairability="suggest_only",
            gate_action="ratchet",
            artifact_policy="full_adg_report",
            signal_source="canonical_policy",
            evidence_tier="truth",
        ),
        notes="H3: migrating from _adg_ci_gates.py M2. Blocks getattr_dynamic delta > 0.",
    ),
    GateCatalogEntry(
        gate_id="G-M3-MUTATION",
        file="ops_scripts/ci/adg_gates/gate_m3_mutation_sovereignty.py",
        cls="M3MutationSovereigntyGate",
        severity="P1",
        gate_class="hygiene",
        policy=ExecutionPolicy(
            stage="full",
            repairability="manual_only",
            gate_action="ratchet",
            artifact_policy="full_adg_report",
            signal_source="canonical_policy",
            evidence_tier="truth",
        ),
        notes="H3: migrating from _adg_ci_gates.py M3. Blocks writes_to delta > 0.",
    ),
    GateCatalogEntry(
        gate_id="G-M4-GUARDRAIL",
        file="ops_scripts/ci/adg_gates/gate_m4_guardrail_coverage.py",
        cls="M4GuardrailCoverageGate",
        severity="P1",
        gate_class="hygiene",
        policy=ExecutionPolicy(
            stage="full",
            repairability="suggest_only",
            gate_action="ratchet",
            artifact_policy="full_adg_report",
            signal_source="canonical_policy",
            evidence_tier="truth",
        ),
        notes="H3: migrating from _adg_ci_gates.py M4. Enforces after W3.",
    ),
    GateCatalogEntry(
        gate_id="G-M5-TRACE",
        file="ops_scripts/ci/adg_gates/gate_m5_trace_coverage.py",
        cls="M5TraceCoverageGate",
        severity="P1",
        gate_class="hygiene",
        policy=ExecutionPolicy(
            stage="full",
            repairability="suggest_only",
            gate_action="ratchet",
            artifact_policy="full_adg_report",
            signal_source="canonical_policy",
            evidence_tier="truth",
        ),
        notes="H3: migrating from _adg_ci_gates.py M5. Enforces after W5.",
    ),
    GateCatalogEntry(
        gate_id="G-M6-REPLAY",
        file="ops_scripts/ci/adg_gates/gate_m6_replay_key.py",
        cls="M6ReplayKeyGate",
        severity="P1",
        gate_class="hygiene",
        policy=ExecutionPolicy(
            stage="full",
            repairability="manual_only",
            gate_action="ratchet",
            artifact_policy="full_adg_report",
            signal_source="canonical_policy",
            evidence_tier="truth",
        ),
        notes="H3: migrating from _adg_ci_gates.py M6. Enforces after W4.",
    ),
    # -----------------------------------------------------------------------
    # P1 — architecture witness tier (Class A positive / Class B absence)
    # -----------------------------------------------------------------------
    GateCatalogEntry(
        gate_id="G-P1-ARCH-WITNESS",
        file="ops_scripts/ci/adg_gates/gate_p1_architecture_witness.py",
        cls="ArchitectureWitnessGate",
        severity="P1",
        gate_class="structural_conformance",
        policy=ExecutionPolicy(
            stage="full",
            repairability="manual_only",
            gate_action="halt",
            artifact_policy="full_adg_report",
            signal_source="sqlite_mv_ci",
            evidence_tier="truth",
        ),
        notes=(
            "Class A: required-live families fail if runtime-orphaned. "
            "Class B: absence families require governing breach view. "
            "Planned families warn-only (not yet blocking)."
        ),
    ),
    # -----------------------------------------------------------------------
    # P1 — harden gate + skip ratchet (legacy standalone)
    # -----------------------------------------------------------------------
    GateCatalogEntry(
        gate_id="G-P1-HARDEN",
        file="ops_scripts/ci/adg_harden_gate.py",
        cls=None,
        severity="P1",
        gate_class="hygiene",
        policy=ExecutionPolicy(
            stage="full",
            repairability="suggest_only",
            gate_action="ratchet",
            artifact_policy="full_adg_report",
            signal_source="canonical_policy",
            evidence_tier="truth",
        ),
        notes="Legacy standalone gate. Anti-pattern count ratchet.",
    ),
    GateCatalogEntry(
        gate_id="G-P1-SKIP",
        file="ops_scripts/ci/adg_skip_file_ratchet.py",
        cls=None,
        severity="P1",
        gate_class="hygiene",
        policy=ExecutionPolicy(
            stage="full",
            repairability="suggest_only",
            gate_action="ratchet",
            artifact_policy="full_adg_report",
            signal_source="canonical_policy",
            evidence_tier="truth",
        ),
        notes="Legacy standalone gate. Ratchets pytest skip annotations.",
    ),
    # -----------------------------------------------------------------------
    # P2 — drift + burndown + centrality (legacy standalone)
    # -----------------------------------------------------------------------
    GateCatalogEntry(
        gate_id="G-P2-DRIFT",
        file="ops_scripts/ci/drift_ratchet_gate.py",
        cls=None,
        severity="P2",
        gate_class="hygiene",
        policy=ExecutionPolicy(
            stage="full",
            repairability="suggest_only",
            gate_action="ratchet",
            artifact_policy="trend_only",
            signal_source="canonical_policy",
            evidence_tier="truth",
        ),
        notes="Broad ratchet — count + concentration_spike block condition.",
    ),
    GateCatalogEntry(
        gate_id="G-P2-BURNDOWN",
        file="ops_scripts/ci/adg_burndown_gate.py",
        cls=None,
        severity="P2",
        gate_class="hygiene",
        policy=ExecutionPolicy(
            stage="full",
            repairability="suggest_only",
            gate_action="watch",
            artifact_policy="trend_only",
            signal_source="canonical_policy",
            evidence_tier="truth",
        ),
        notes="Watch only. Tracks violation burndown trend.",
    ),
    GateCatalogEntry(
        gate_id="G-P2-CENTRALITY",
        file="ops_scripts/ci/centrality_gate.py",
        cls=None,
        severity="P2",
        gate_class="hygiene",
        policy=ExecutionPolicy(
            stage="full",
            repairability="suggest_only",
            gate_action="watch",
            artifact_policy="neighborhood_artifact",
            signal_source="canonical_policy",
            evidence_tier="truth",
        ),
        notes="Watch only. Emits neighborhood artifact for blast-radius investigation.",
    ),
    # -----------------------------------------------------------------------
    # P3 — trend + promotion (legacy standalone)
    # -----------------------------------------------------------------------
    GateCatalogEntry(
        gate_id="G-P3-FANIN",
        file="ops_scripts/ci/adg_fanin_triage_gate.py",
        cls=None,
        severity="P3",
        gate_class="hygiene",
        policy=ExecutionPolicy(
            stage="full",
            repairability="suggest_only",
            gate_action="watch",
            artifact_policy="trend_only",
            signal_source="canonical_policy",
            evidence_tier="truth",
        ),
        notes="Watch only. Tracks fan-in growth + promotion candidates.",
    ),
]


# ---------------------------------------------------------------------------
# Catalog index and validation
# ---------------------------------------------------------------------------


def build_index() -> dict[str, GateCatalogEntry]:
    """Build a gate_id → entry index and validate all entries."""
    index: dict[str, GateCatalogEntry] = {}
    errors: list[str] = []

    for entry in GATE_CATALOG:
        if entry.gate_id in index:
            errors.append(f"Duplicate gate_id: {entry.gate_id}")
        else:
            index[entry.gate_id] = entry

        entry_errors = entry.validate()
        for err in entry_errors:
            errors.append(f"{entry.gate_id}: {err}")

    if errors:
        raise ValueError(
            f"Gate SSOT catalog has {len(errors)} validation error(s):\n"
            + "\n".join(f"  - {e}" for e in errors)
        )

    return index


def get_gates_by_severity(severity: str) -> list[GateCatalogEntry]:
    """Return all catalog entries for a given severity level."""
    return [e for e in GATE_CATALOG if e.severity == severity]


def get_preflight_gates() -> list[GateCatalogEntry]:
    """Return gates that support preflight mode."""
    return [e for e in GATE_CATALOG if "preflight" in e.policy.stage]


def get_full_gates() -> list[GateCatalogEntry]:
    """Return gates that run in full mode (includes preflight+full gates)."""
    return [e for e in GATE_CATALOG if "full" in e.policy.stage]


# Validate catalog at import time — fail loudly if entries are invalid.
GATE_INDEX: dict[str, GateCatalogEntry] = build_index()
