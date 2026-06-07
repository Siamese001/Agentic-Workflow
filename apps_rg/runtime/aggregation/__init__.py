"""Final resume aggregation hardening (W1–W4): fingerprint, proof refs, cross-section X2."""

from apps_rg.runtime.aggregation.cross_section_x2 import (
    CrossSectionGateResult,
    build_overlap_artifacts,
    build_cross_section_graph_coherence_receipt,
    check_cross_section_graph_coherence,
    cross_section_fail_gate_ids,
    cross_section_gates_all_pass,
    run_cross_section_x2_gates,
)
from apps_rg.runtime.aggregation.preflight import (
    AggregationPreflightError,
    run_aggregation_preflight,
)
from apps_rg.runtime.aggregation.run_fingerprint import build_orchestration_fingerprint
from apps_rg.runtime.aggregation.section_sealed_index import build_section_sealed_index

__all__ = [
    "AggregationPreflightError",
    "CrossSectionGateResult",
    "build_cross_section_graph_coherence_receipt",
    "build_orchestration_fingerprint",
    "build_overlap_artifacts",
    "build_section_sealed_index",
    "check_cross_section_graph_coherence",
    "cross_section_fail_gate_ids",
    "cross_section_gates_all_pass",
    "run_aggregation_preflight",
    "run_cross_section_x2_gates",
]
