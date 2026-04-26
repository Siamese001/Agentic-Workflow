"""C0.6 CONTROLLED REFINEMENT LOOP.

Spec: C0 Context Engine.md lines 694-739. Pure-data planner; emits a
refinement *intent* (not the second-pass results — those flow back through
shape/contract). Hard NOs from spec lines 717-724 are enforced.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .contradiction_gap import ConflictGapReport
from .evidence_contract import EvidenceContract
from .plan import RetrievalPlan
from .verdicts import GapType, RefineTactic, SupportStatus


_REFINE_ENTRY_STATUSES: frozenset[SupportStatus] = frozenset({
    SupportStatus.WEAK,
    SupportStatus.WEAK_WITH_CAVEATS,
    SupportStatus.CONFLICTED,
    SupportStatus.EMPTY,
})


@dataclass(frozen=True)
class RefineDiagnostic:
    """Spec lines 644-654 — diagnose what to refine."""

    wrong_terms: bool = False
    query_too_narrow: bool = False
    query_too_broad: bool = False
    stale_sources: bool = False
    missing_graph_neighbor: bool = False
    source_class_omitted: bool = False
    exact_phrase_missing: bool = False
    contradiction_present: bool = False
    acl_blocked: bool = False
    support_target_compound: bool = False

    def any(self) -> bool:
        return any(
            (
                self.wrong_terms, self.query_too_narrow, self.query_too_broad,
                self.stale_sources, self.missing_graph_neighbor,
                self.source_class_omitted, self.exact_phrase_missing,
                self.contradiction_present, self.acl_blocked,
                self.support_target_compound,
            )
        )


@dataclass(frozen=True)
class RefinedEvidenceContract:
    """Spec line 736 — augmented contract carrying refinement metadata."""

    base_contract: EvidenceContract
    refine_attempts: int
    refine_tactic: RefineTactic
    diagnostic: RefineDiagnostic
    refine_delta_score: float = 0.0  # post-refine support_score - pre
    remaining_gap_codes: tuple[str, ...] = field(default_factory=tuple)
    bypass_reason: str = ""  # set when refinement was not attempted

    def __post_init__(self) -> None:
        if self.refine_attempts < 0:
            raise ValueError("refine_attempts must be >= 0")
        if not -1.0 <= self.refine_delta_score <= 1.0:
            raise ValueError("refine_delta_score must be in [-1,1]")


_COMPOUND_TASK_MARKERS: tuple[str, ...] = (
    " and ", " AND ", " & ", "; and ",
    " plus ", " also ", " in addition ",
    " as well as ", " along with ",
)


def detect_compound_target(task_spec: str) -> bool:
    """Heuristic for spec line 654 (`support_target_compound`).

    A task is "compound" when it asks for two or more orthogonal claims that
    cannot be answered by a single citation. The cheap signal is conjunctive
    language plus multiple distinct interrogatives. Callers can override by
    passing the result to plan_refinement(..., compound_target=...).
    """
    if not task_spec:
        return False
    lower = task_spec.strip()
    if lower.count("?") >= 2:
        return True
    return any(marker in task_spec for marker in _COMPOUND_TASK_MARKERS)


def _diagnose(
    contract: EvidenceContract,
    conflict: ConflictGapReport,
    *,
    compound_target: bool = False,
) -> RefineDiagnostic:
    gap_codes = {g.gap_type for g in conflict.gaps}
    return RefineDiagnostic(
        wrong_terms=GapType.MISSING_DIRECT_SUPPORT in gap_codes
        and contract.score_breakdown.coverage_score < 0.3,
        query_too_narrow=GapType.MISSING_SOURCE_DIVERSITY in gap_codes,
        query_too_broad=contract.support_score < 0.30 and len(contract.verified_chunk_ids) > 20,
        stale_sources=GapType.MISSING_CURRENT_VERSION in gap_codes,
        missing_graph_neighbor=GapType.MISSING_VALIDATION in gap_codes,
        source_class_omitted=GapType.MISSING_VALIDATION in gap_codes,
        exact_phrase_missing=GapType.MISSING_EXACT_QUOTE in gap_codes,
        contradiction_present=bool(contract.contradiction_chunk_pairs),
        acl_blocked=GapType.MISSING_TENANT_PROOF in gap_codes,
        support_target_compound=compound_target,
    )


def _choose_tactic(
    diag: RefineDiagnostic,
    plan: RetrievalPlan,
    conflict: ConflictGapReport,
) -> RefineTactic:
    """Spec lines 656-664 — eight tactics."""
    # ABSTAIN trumps everything when ACL is blocked (HARD NO from spec line 720).
    if diag.acl_blocked:
        return RefineTactic.ABSTAIN
    if conflict.recommended_refine_tactic is not None:
        return conflict.recommended_refine_tactic
    if diag.exact_phrase_missing:
        return RefineTactic.HYBRIDIZE
    if diag.stale_sources:
        return RefineTactic.FRESHEN
    if diag.query_too_narrow:
        return RefineTactic.BROADEN
    if diag.query_too_broad:
        return RefineTactic.NARROW
    if diag.support_target_compound:
        return RefineTactic.DECOMPOSE
    if diag.missing_graph_neighbor and plan.graph_bounds.max_hops > 0:
        return RefineTactic.GRAPH_HOP
    if diag.wrong_terms:
        return RefineTactic.REWRITE
    return RefineTactic.REWRITE


def plan_refinement(
    contract: EvidenceContract,
    *,
    conflict: ConflictGapReport,
    plan: RetrievalPlan,
    attempts_so_far: int,
    compound_target: bool = False,
) -> RefinedEvidenceContract:
    """Decide whether/how to refine. Returns a RefinedEvidenceContract.

    HARD GUARDS (spec lines 717-724):
      - cannot exceed plan.budgets.max_refine_attempts
      - cannot change the user task or route
      - cannot expand tenant / ACL / region
      - cannot ignore contradictions
      - ABSTAIN tactic is sticky once chosen

    `compound_target` (spec line 654): pass True when the upstream task_spec
    is judged to require multiple distinct citations. When True, DECOMPOSE
    becomes a candidate tactic. Callers can use ``detect_compound_target``
    or supply their own classifier.
    """
    diag = _diagnose(contract, conflict, compound_target=compound_target)

    # Entry conditions (spec lines 700-705)
    if contract.status not in _REFINE_ENTRY_STATUSES:
        return RefinedEvidenceContract(
            base_contract=contract,
            refine_attempts=attempts_so_far,
            refine_tactic=RefineTactic.REWRITE,
            diagnostic=diag,
            refine_delta_score=0.0,
            remaining_gap_codes=contract.unresolved_gap_codes,
            bypass_reason=f"status={contract.status.value} does not require refinement",
        )

    if attempts_so_far >= plan.budgets.max_refine_attempts:
        return RefinedEvidenceContract(
            base_contract=contract,
            refine_attempts=attempts_so_far,
            refine_tactic=RefineTactic.ABSTAIN,
            diagnostic=diag,
            refine_delta_score=0.0,
            remaining_gap_codes=contract.unresolved_gap_codes,
            bypass_reason=(
                f"refine budget exhausted: attempts={attempts_so_far} "
                f"max={plan.budgets.max_refine_attempts}"
            ),
        )

    if not diag.any() and not contract.contradiction_chunk_pairs:
        return RefinedEvidenceContract(
            base_contract=contract,
            refine_attempts=attempts_so_far,
            refine_tactic=RefineTactic.ABSTAIN,
            diagnostic=diag,
            refine_delta_score=0.0,
            remaining_gap_codes=contract.unresolved_gap_codes,
            bypass_reason="no diagnosable gap or contradiction",
        )

    tactic = _choose_tactic(diag, plan, conflict)
    return RefinedEvidenceContract(
        base_contract=contract,
        refine_attempts=attempts_so_far + 1,
        refine_tactic=tactic,
        diagnostic=diag,
        refine_delta_score=0.0,  # caller updates after second pass
        remaining_gap_codes=contract.unresolved_gap_codes,
        bypass_reason="",
    )


__all__ = [
    "RefineDiagnostic",
    "RefinedEvidenceContract",
    "detect_compound_target",
    "plan_refinement",
]
