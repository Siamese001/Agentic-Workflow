"""ADG Materialized-View-Driven CI Gates.

15 gate families across P0/P1/P2 severity levels:
    Phase A - P0 Hard-Block Gates (1-6):
        1. critical_path_integrity
        2. authority_boundary
        3. write_sovereignty
        4. capability_egress
        5. text_to_action
        6. determinism_provenance

    Phase B - P1 Ratchet Gates (7-12):
        7. lifecycle_coverage
        8. trace_replay_eval
        9. tool_provider_ambiguity
        10. agent_shape
        11. task_contract
        12. modified_area_regression

    Phase C - P2 Watch/Promotion Gates (13-15):
        13. exemption_proximity
        14. hotspot_concentration
        15. taxonomy_orphan

Usage:
    python -m ops_scripts.ci.adg_gates run-all          # Run all gates
    python -m ops_scripts.ci.adg_gates run-phase A    # Run Phase A gates only
    python -m ops_scripts.ci.adg_gates run-gate 1,3,5 # Run specific gates
    python -m ops_scripts.ci.adg_gates list            # List all gates
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

from ops_scripts.ci.adg_gates.gate_base import ADGGateBase, GateResult, GateViolation
from ops_scripts.ci.adg_gates.gate_p0_critical_path import CriticalPathIntegrityGate
from ops_scripts.ci.adg_gates.gate_p0_authority import AuthorityBoundaryGate
from ops_scripts.ci.adg_gates.gate_p0_write_sovereignty import WriteSovereigntyGate
from ops_scripts.ci.adg_gates.gate_p0_capability_egress import CapabilityEgressGate
from ops_scripts.ci.adg_gates.gate_p0_text_to_action import TextToActionGate
from ops_scripts.ci.adg_gates.gate_p0_determinism import DeterminismProvenanceGate
from ops_scripts.ci.adg_gates.gate_p1_lifecycle import LifecycleCoverageGate
from ops_scripts.ci.adg_gates.gate_p1_trace_replay import TraceReplayEvalGate
from ops_scripts.ci.adg_gates.gate_p1_architecture_witness import ArchitectureWitnessGate
from ops_scripts.ci.adg_gates.gate_p1_prompt_wiring import PromptAssemblyWiringGate
from ops_scripts.ci.adg_gates.gate_executor_theater import ExecutorTheaterGate
from ops_scripts.ci.adg_gates.gate_infra_wiring import InfraWiringGate

__all__ = [
    "ADGGateBase",
    "GateResult",
    "GateViolation",
    "GATE_REGISTRY",
    # P0 Gates
    "CriticalPathIntegrityGate",
    "AuthorityBoundaryGate",
    "WriteSovereigntyGate",
    "CapabilityEgressGate",
    "TextToActionGate",
    "DeterminismProvenanceGate",
    "ExecutorTheaterGate",
    "InfraWiringGate",
    # P1 Gates
    "LifecycleCoverageGate",
    "TraceReplayEvalGate",
    "ArchitectureWitnessGate",
    "PromptAssemblyWiringGate",
]

# Gate registry: gate_id -> (class, phase, severity)
# Gates 9+ added 2026-04-19 to surface existing ADG gate classes that were
# present on disk but previously unreachable via CLI (run-all / run-phase /
# list). Registration here is the canonical discovery point; p0_runner.py
# holds the separate two-pass orchestration list for P0 blocking.
GATE_REGISTRY: dict[str, tuple[type[ADGGateBase], str, str]] = {
    # Phase A: P0 Hard-Block
    "1": (CriticalPathIntegrityGate, "A", "P0"),
    "2": (AuthorityBoundaryGate, "A", "P0"),
    "3": (WriteSovereigntyGate, "A", "P0"),
    "4": (CapabilityEgressGate, "A", "P0"),
    "5": (TextToActionGate, "A", "P0"),
    "6": (DeterminismProvenanceGate, "A", "P0"),
    "9": (ExecutorTheaterGate, "A", "P0"),
    "10": (InfraWiringGate, "A", "P0"),
    # Phase B: P1 Ratchet
    "7": (LifecycleCoverageGate, "B", "P1"),
    "8": (TraceReplayEvalGate, "B", "P1"),
    "11": (ArchitectureWitnessGate, "B", "P1"),
    "12": (PromptAssemblyWiringGate, "B", "P1"),
}


def get_gate(gate_id: str) -> ADGGateBase | None:
    """Get gate instance by ID."""
    if gate_id not in GATE_REGISTRY:
        return None
    gate_class, _, _ = GATE_REGISTRY[gate_id]
    return gate_class()


def list_gates() -> dict[str, dict]:
    """List all available gates with metadata."""
    result = {}
    for gate_id, (gate_class, phase, severity) in GATE_REGISTRY.items():
        instance = gate_class()
        result[gate_id] = {
            "family": instance.gate_family,
            "phase": phase,
            "severity": severity,
            "source_views": instance.source_views,
        }
    return result


def run_phase(phase: str, emit_artifacts: bool = True) -> dict[str, GateResult]:
    """Run all gates in a phase."""
    results = {}
    for gate_id, (gate_class, gate_phase, _) in GATE_REGISTRY.items():
        if gate_phase == phase.upper():
            gate = gate_class()
            results[gate_id] = gate.run(emit_artifacts=emit_artifacts)
    return results


def run_all(emit_artifacts: bool = True) -> dict[str, GateResult]:
    """Run all gates."""
    results = {}
    for gate_id in sorted(GATE_REGISTRY.keys(), key=int):
        gate_class, _, _ = GATE_REGISTRY[gate_id]
        gate = gate_class()
        results[gate_id] = gate.run(emit_artifacts=emit_artifacts)
    return results
