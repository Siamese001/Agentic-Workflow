"""C0 invariants (I1..I12), quality gates (G0..G10), failure-mode catalog.

Spec: ``docs/reference/03_L0_Routing/C0 - Retrieval/C0 Context Engine.md``
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Final

from agentic_core.L1_cognition.c0_context.types import (
    FAILURE_MODES,
    QUALITY_GATES,
    EvidenceItem,
    FinalEvidenceContract,
    SupportStatus,
)


# ---------------------------------------------------------------------------
# Invariants C0.I1..C0.I12 — predicates over a FinalEvidenceContract.
# ---------------------------------------------------------------------------


class InvariantViolationError(RuntimeError):
    """Raised when a runtime check finds a violated C0 invariant."""


def i1_retrieval_only(contract: FinalEvidenceContract) -> bool:
    """C0.I1 — C0 never writes final prose as the answer.

    Approximation: the contract carries no field named ``final_answer``
    in its ``extras``.
    """
    return "final_answer" not in contract.extras


def i2_retrieved_data_not_instruction(extras: dict[str, str]) -> bool:
    """C0.I2 — retrieved text is data, never instruction.

    Caller asserts ``content_classification`` in extras is ``data``.
    """
    return extras.get("content_classification", "data") == "data"


def i3_lineage_preserved(item: EvidenceItem) -> bool:
    """C0.I3 — every retrieved item preserves source_id, version, ACL, lane."""
    return bool(item.source_id) and bool(item.acl_status) and bool(item.retrieval_lane)


def i4_dense_alone_not_enough_for_high_stakes(
    *,
    high_stakes: bool,
    retrieval_lanes_used: frozenset[str],
) -> bool:
    """C0.I4 — dense alone is not enough for high-stakes claims."""
    if not high_stakes:
        return True
    return retrieval_lanes_used != frozenset({"dense"})


def i5_exact_claims_need_sparse_or_metadata(
    *,
    has_exact_claim: bool,
    retrieval_lanes_used: frozenset[str],
) -> bool:
    """C0.I5 — exact names/IDs/paths/labels need sparse/BM25 or metadata."""
    if not has_exact_claim:
        return True
    return bool(retrieval_lanes_used & {"sparse", "metadata"})


def i6_graph_bounded(*, hops_used: int, max_hops: int) -> bool:
    """C0.I6 — graph expansion is bounded."""
    return 0 <= hops_used <= max_hops


def i7_contradictions_surfaced(contract: FinalEvidenceContract) -> bool:
    """C0.I7 — contradictions must be surfaced. CONFLICTED status implies flags."""
    if contract.status == SupportStatus.CONFLICTED:
        return len(contract.contradiction_flags) > 0
    return True


def i8_weak_evidence_stays_weak(contract: FinalEvidenceContract) -> bool:
    """C0.I8 — weak evidence cannot be inflated.

    If status is WEAK / WEAK_WITH_CAVEATS, support_score must be < 0.85.
    """
    if contract.status in {SupportStatus.WEAK, SupportStatus.WEAK_WITH_CAVEATS}:
        return contract.support_score < 0.85
    return True


def i9_one_refine_loop(contract: FinalEvidenceContract, *, max_attempts: int) -> bool:
    """C0.I9 — at most one refinement loop within budget."""
    return 0 <= contract.refine_attempts <= max_attempts


def i10_no_self_authorize_route(contract: FinalEvidenceContract) -> bool:
    """C0.I10 — C0 may recommend reroute but cannot self-authorize."""
    return "self_authorized_route_change" not in contract.extras


def i11_output_is_contract_not_answer(contract: FinalEvidenceContract) -> bool:
    """C0.I11 — output is a contract, not an answer."""
    return "final_answer_text" not in contract.extras


def i12_only_verified_to_prompt_assembly(contract: FinalEvidenceContract) -> bool:
    """C0.I12 — Prompt Assembly receives only verified context.

    Approximation: every evidence item must have non-empty acl_status.
    """
    return all(bool(item.acl_status) for item in contract.evidence)


def assert_all_invariants(
    contract: FinalEvidenceContract,
    *,
    high_stakes: bool = False,
    retrieval_lanes_used: frozenset[str] = frozenset({"dense", "sparse"}),
    has_exact_claim: bool = False,
    hops_used: int = 0,
    max_hops: int = 3,
    max_refine_attempts: int = 1,
) -> None:
    """Run every invariant against ``contract``. Raises on first violation."""
    checks: list[tuple[str, bool]] = [
        ("C0.I1", i1_retrieval_only(contract)),
        ("C0.I2", i2_retrieved_data_not_instruction(contract.extras)),
        ("C0.I4", i4_dense_alone_not_enough_for_high_stakes(
            high_stakes=high_stakes, retrieval_lanes_used=retrieval_lanes_used)),
        ("C0.I5", i5_exact_claims_need_sparse_or_metadata(
            has_exact_claim=has_exact_claim, retrieval_lanes_used=retrieval_lanes_used)),
        ("C0.I6", i6_graph_bounded(hops_used=hops_used, max_hops=max_hops)),
        ("C0.I7", i7_contradictions_surfaced(contract)),
        ("C0.I8", i8_weak_evidence_stays_weak(contract)),
        ("C0.I9", i9_one_refine_loop(contract, max_attempts=max_refine_attempts)),
        ("C0.I10", i10_no_self_authorize_route(contract)),
        ("C0.I11", i11_output_is_contract_not_answer(contract)),
        ("C0.I12", i12_only_verified_to_prompt_assembly(contract)),
    ]
    # I3 runs per-item
    for item in contract.evidence:
        if not i3_lineage_preserved(item):
            raise InvariantViolationError(
                f"C0.I3 violated for evidence_id={item.evidence_id!r}",
            )
    for label, ok in checks:
        if not ok:
            raise InvariantViolationError(f"{label} violated")


# ---------------------------------------------------------------------------
# Quality gates G0..G10 — fail-action: return reason string when blocked.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GateOutcome:
    gate_id: str
    passed: bool
    reason: str = ""


def gate_g0_scope(*, route_allows_retrieval: bool) -> GateOutcome:
    return GateOutcome("C0.G0_Scope", route_allows_retrieval,
                       "" if route_allows_retrieval else "BLOCKED — route does not allow C0 retrieval")


def gate_g1_acl(*, all_sources_acl_cleared: bool) -> GateOutcome:
    return GateOutcome("C0.G1_ACL", all_sources_acl_cleared,
                       "" if all_sources_acl_cleared else "ACL violation — exclude or BLOCKED")


def gate_g2_fresh(*, freshness_satisfied: bool) -> GateOutcome:
    return GateOutcome("C0.G2_Fresh", freshness_satisfied,
                       "" if freshness_satisfied else "stale evidence — search newer or caveat")


def gate_g3_exact(*, has_exact_claim: bool, sparse_or_metadata_present: bool) -> GateOutcome:
    ok = (not has_exact_claim) or sparse_or_metadata_present
    return GateOutcome("C0.G3_Exact", ok,
                       "" if ok else "exact claim without sparse/metadata support → WEAK")


def gate_g4_dense(*, dense_relevance_score: float, threshold: float = 0.30) -> GateOutcome:
    ok = dense_relevance_score >= threshold
    return GateOutcome("C0.G4_Dense", ok,
                       "" if ok else f"dense relevance {dense_relevance_score:.2f} < {threshold}")


def gate_g5_graph(*, hops_used: int, max_hops: int) -> GateOutcome:
    ok = 0 <= hops_used <= max_hops
    return GateOutcome("C0.G5_Graph", ok,
                       "" if ok else f"graph hops {hops_used} > max {max_hops}")


def gate_g6_cite(*, all_anchors_resolve: bool) -> GateOutcome:
    return GateOutcome("C0.G6_Cite", all_anchors_resolve,
                       "" if all_anchors_resolve else "citation anchor unresolved")


def gate_g7_conflict(*, contradictions_surfaced: bool) -> GateOutcome:
    return GateOutcome("C0.G7_Conflict", contradictions_surfaced,
                       "" if contradictions_surfaced else "contradictions present but not surfaced")


def gate_g8_cover(*, coverage_score: float, threshold: float = 0.50) -> GateOutcome:
    ok = coverage_score >= threshold
    return GateOutcome("C0.G8_Cover", ok,
                       "" if ok else f"coverage {coverage_score:.2f} < {threshold} — refine or WEAK")


def gate_g9_budget(*, must_use_fits_budget: bool) -> GateOutcome:
    return GateOutcome("C0.G9_Budget", must_use_fits_budget,
                       "" if must_use_fits_budget else "must-use evidence does not fit token budget")


def gate_g10_inject(*, retrieved_text_classified_data: bool) -> GateOutcome:
    return GateOutcome("C0.G10_Inject", retrieved_text_classified_data,
                       "" if retrieved_text_classified_data else "retrieved text not classified as data")


GATE_FUNCTIONS: Final[dict[str, Callable[..., GateOutcome]]] = {
    "C0.G0_Scope": gate_g0_scope,
    "C0.G1_ACL": gate_g1_acl,
    "C0.G2_Fresh": gate_g2_fresh,
    "C0.G3_Exact": gate_g3_exact,
    "C0.G4_Dense": gate_g4_dense,
    "C0.G5_Graph": gate_g5_graph,
    "C0.G6_Cite": gate_g6_cite,
    "C0.G7_Conflict": gate_g7_conflict,
    "C0.G8_Cover": gate_g8_cover,
    "C0.G9_Budget": gate_g9_budget,
    "C0.G10_Inject": gate_g10_inject,
}


def gates_match_spec_count() -> bool:
    """Sanity — exactly 11 gates per spec."""
    return len(GATE_FUNCTIONS) == 11 and set(GATE_FUNCTIONS.keys()) == set(QUALITY_GATES)


# ---------------------------------------------------------------------------
# Failure-mode prevention catalog.
# ---------------------------------------------------------------------------


FAILURE_MODE_PREVENTIONS: Final[dict[str, str]] = {
    "dense_only_hallucination": "require sparse/metadata confirmation for exact claims (G3+I5)",
    "wrong_tenant_evidence": "ACL+tenant filters at plan/fetch/graph hop/verification (G1+I12)",
    "stale_policy_answer": "freshness_class check + version verification (G2)",
    "quote_distortion": "parent expansion + stable cited span verification (G6)",
    "hidden_contradiction": "contradiction scan + CONTRADICTS evidence class (I7+G7)",
    "graph_scope_creep": "max_hops + relation filter + ACL at every hop (I6+G5)",
    "cache_poisoning": "cache lineage verification + freshness/policy gates (G2)",
    "prompt_injection_via_retrieved_text": "origin-trust labeling + data-only wrapping (I2+G10)",
    "fake_confidence": "score breakdown + unresolved gaps + WEAK_WITH_CAVEATS (I8)",
    "lost_lineage": "retrieval_mode_provenance + lineage_manifest (I3)",
    "overstuffed_context": "priority packing + deterministic trim order (G9)",
    "unsupported_synthesis": "distinguish direct support from inference risk (score breakdown)",
    "docs_vs_code_mismatch": "surface conflict; do not silently prefer convenient source (G7)",
    "runtime_vs_design_mismatch": "include trace/log evidence as contradiction or validation (G7)",
}


def failure_modes_match_spec_count() -> bool:
    """Sanity — exactly 14 failure modes per spec."""
    return (
        len(FAILURE_MODE_PREVENTIONS) == 14
        and set(FAILURE_MODE_PREVENTIONS.keys()) == set(FAILURE_MODES)
    )


__all__ = [
    "FAILURE_MODE_PREVENTIONS",
    "GATE_FUNCTIONS",
    "GateOutcome",
    "InvariantViolationError",
    "assert_all_invariants",
    "failure_modes_match_spec_count",
    "gate_g0_scope",
    "gate_g10_inject",
    "gate_g1_acl",
    "gate_g2_fresh",
    "gate_g3_exact",
    "gate_g4_dense",
    "gate_g5_graph",
    "gate_g6_cite",
    "gate_g7_conflict",
    "gate_g8_cover",
    "gate_g9_budget",
    "gates_match_spec_count",
    "i10_no_self_authorize_route",
    "i11_output_is_contract_not_answer",
    "i12_only_verified_to_prompt_assembly",
    "i1_retrieval_only",
    "i2_retrieved_data_not_instruction",
    "i3_lineage_preserved",
    "i4_dense_alone_not_enough_for_high_stakes",
    "i5_exact_claims_need_sparse_or_metadata",
    "i6_graph_bounded",
    "i7_contradictions_surfaced",
    "i8_weak_evidence_stays_weak",
    "i9_one_refine_loop",
]
