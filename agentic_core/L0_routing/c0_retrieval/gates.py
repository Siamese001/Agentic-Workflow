"""C0 QUALITY GATES — G0..G10.

Spec: C0 Context Engine.md lines 906-923 (gate table) + 929-946 (failure modes).

Each gate is a pure predicate that inspects the inputs available at the gate's
position in the pipeline and returns a `GateOutcome`. Gates do NOT mutate
state; they return verdicts the dispatcher uses to:
  - block the run (BLOCKED status + blocked_reason)
  - downgrade the contract (PASS -> WEAK / WEAK_WITH_CAVEATS / CONFLICTED)
  - prune evidence (return excluded_with_reasons additions)

Wiring expectation:
  G0 — preflight stage  (run_preflight already encodes G0 + G10 partial)
  G1 — fetch / hydrate stage (per-chunk ACL clear)
  G2 — hydration / contract stage (freshness vs route.freshness_class)
  G3 — contract stage (exact targets demand sparse/metadata lane)
  G4 — shape stage (semantic relevance threshold)
  G5 — graph stage (max_hops + relation_filter respected)
  G6 — hydration / contract stage (citation anchor stable)
  G7 — contradiction_gap stage (contradictions surfaced)
  G8 — contract stage (coverage of support_target)
  G9 — final pack (must_keep fits in budget)
  G10 — preflight + fetch (instruction-payload quarantine)

The dispatcher invokes `run_all_gates(...)` to produce a single `GateReport`
that is folded into the FinalEvidenceContract for replay/audit.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .candidate_pool import CandidateChunk, CandidateEvidencePool
from .contradiction_gap import ConflictGapReport
from .evidence_contract import EvidenceContract
from .graph_traverse import GraphExpandedEvidencePool
from .hydration import HydratedChunk, HydratedEvidencePool
from .injection import detect_injection_markers
from .plan import RetrievalPlan
from .preflight import C0PreflightStatus
from .route_contract import L1PlanContract, RouteContract
from .shape import ShapedEvidenceSet
from .verdicts import (
    EXACTNESS_REQUIRED,
    C0Gate,
    FreshnessClass,
    RetrievalLane,
    RetrievalMode,
    SupportStatus,
)


@dataclass(frozen=True)
class GateOutcome:
    """One gate verdict — passed or not, with audit reason."""

    gate: C0Gate
    passed: bool
    reason: str
    severity: str = "info"  # info | warn | block
    affected_chunk_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.severity not in ("info", "warn", "block"):
            raise ValueError(f"invalid severity {self.severity!r}")


@dataclass(frozen=True)
class GateReport:
    """All gate outcomes for one C0 run."""

    plan_id: str
    outcomes: tuple[GateOutcome, ...]

    def by_gate(self, g: C0Gate) -> GateOutcome | None:
        for o in self.outcomes:
            if o.gate == g:
                return o
        return None

    def all_passed(self) -> bool:
        return all(o.passed for o in self.outcomes)

    def blockers(self) -> tuple[GateOutcome, ...]:
        return tuple(o for o in self.outcomes if o.severity == "block" and not o.passed)

    def warnings(self) -> tuple[GateOutcome, ...]:
        return tuple(o for o in self.outcomes if o.severity == "warn" and not o.passed)


# ----- individual gates -----


def G0_scope(
    *, route: RouteContract, plan: L1PlanContract, preflight: C0PreflightStatus,
) -> GateOutcome:
    """G0 SCOPE — Is C0 allowed to retrieve for this route?

    Fail behavior: BLOCKED / recommend R5 or reroute.
    """
    if preflight.eligible:
        return GateOutcome(C0Gate.G0_SCOPE, True, "C0 retrieval permitted by route")
    reason = (
        f"preflight blocked: {preflight.blocked_reason.value if preflight.blocked_reason else 'unknown'}"
    )
    return GateOutcome(C0Gate.G0_SCOPE, False, reason, severity="block")


def G1_acl(
    *, hydrated: HydratedEvidencePool, route: RouteContract,
) -> GateOutcome:
    """G1 ACL — Is every source tenant/region/data-class cleared?

    Fail behavior: Exclude source or BLOCKED. We exclude per-chunk; only when
    EVERY chunk fails do we mark the whole gate as block-severity.
    """
    bad: list[str] = []
    for h in hydrated.hydrated:
        m = h.candidate.manifest
        if not h.quality.acl_clear:
            bad.append(h.candidate.chunk_id)
            continue
        if route.tenant_scope and m.tenant and m.tenant != route.tenant_scope:
            bad.append(h.candidate.chunk_id)
            continue
        if route.region and m.region and m.region != route.region:
            bad.append(h.candidate.chunk_id)
            continue
        if not route.allows_data_class(m.data_class):
            bad.append(h.candidate.chunk_id)
    if not bad:
        return GateOutcome(C0Gate.G1_ACL, True, "all chunks ACL-cleared")
    if len(bad) == len(hydrated.hydrated):
        return GateOutcome(
            C0Gate.G1_ACL, False,
            f"every chunk failed ACL ({len(bad)}/{len(bad)})",
            severity="block", affected_chunk_ids=tuple(bad),
        )
    return GateOutcome(
        C0Gate.G1_ACL, False,
        f"{len(bad)}/{len(hydrated.hydrated)} chunks failed ACL — pruning",
        severity="warn", affected_chunk_ids=tuple(bad),
    )


def G2_fresh(
    *, hydrated: HydratedEvidencePool, route: RouteContract,
) -> GateOutcome:
    """G2 FRESH — Is evidence current enough for freshness_class?

    For LATEST/CURRENT routes, every chunk needs `source_version_current=True`
    or an explicit version stamp. For STATIC/SLOW routes, missing version is
    acceptable.
    """
    fc = route.freshness_class
    if fc in (FreshnessClass.STATIC, FreshnessClass.SLOW):
        return GateOutcome(C0Gate.G2_FRESH, True, f"freshness_class={fc.value} tolerates static")

    stale: list[str] = []
    for h in hydrated.hydrated:
        if not h.quality.source_version_current:
            stale.append(h.candidate.chunk_id)
    if not stale:
        return GateOutcome(C0Gate.G2_FRESH, True, "all chunks current")
    return GateOutcome(
        C0Gate.G2_FRESH, False,
        f"{len(stale)}/{len(hydrated.hydrated)} chunks lack current version stamp",
        severity="warn", affected_chunk_ids=tuple(stale),
    )


def G3_exact(
    *, plan: RetrievalPlan, hydrated: HydratedEvidencePool,
) -> GateOutcome:
    """G3 EXACT — Are exact claims backed by sparse/metadata support?

    For exactness-required targets, at least one chunk must be found via
    SPARSE or METADATA lane. Pure-dense recall is insufficient (C0.I5).
    """
    if plan.support_target not in EXACTNESS_REQUIRED:
        return GateOutcome(C0Gate.G3_EXACT, True, "support_target does not require exactness")
    has_exact_lane = any(
        RetrievalLane.SPARSE in h.candidate.found_by_lanes
        or RetrievalLane.METADATA in h.candidate.found_by_lanes
        or RetrievalLane.CODE in h.candidate.found_by_lanes
        for h in hydrated.hydrated
    )
    if has_exact_lane:
        return GateOutcome(C0Gate.G3_EXACT, True, "sparse/metadata/code lane confirms exactness")
    return GateOutcome(
        C0Gate.G3_EXACT, False,
        f"target={plan.support_target.value} demands exact lane; none found (C0.I5)",
        severity="warn",
    )


def G4_dense(
    *, hydrated: HydratedEvidencePool, min_score: float = 0.30,
) -> GateOutcome:
    """G4 DENSE — Are semantic hits directly relevant?

    Prune chunks whose normalized dense score is below threshold and whose
    only retrieval lane was DENSE.
    """
    weak: list[str] = []
    for h in hydrated.hydrated:
        c = h.candidate
        only_dense = c.found_by_lanes == (RetrievalLane.DENSE,)
        if only_dense and c.scores.normalized_score < min_score:
            weak.append(c.chunk_id)
    if not weak:
        return GateOutcome(C0Gate.G4_DENSE, True, "all dense-only chunks above threshold")
    return GateOutcome(
        C0Gate.G4_DENSE, False,
        f"{len(weak)} dense-only chunks below {min_score} — pruning",
        severity="warn", affected_chunk_ids=tuple(weak),
    )


def G5_graph(
    *, expanded: GraphExpandedEvidencePool, max_hops: int,
) -> GateOutcome:
    """G5 GRAPH — Are graph hops bounded and support-relevant?"""
    over: list[str] = []
    for hop in expanded.traverse.hops:
        if hop.hop_depth > max_hops:
            over.append(hop.dst_chunk_id)
    if not over:
        return GateOutcome(C0Gate.G5_GRAPH, True, f"all hops within max_hops={max_hops}")
    return GateOutcome(
        C0Gate.G5_GRAPH, False,
        f"{len(over)} hop(s) exceeded max_hops={max_hops}",
        severity="block", affected_chunk_ids=tuple(over),
    )


def G6_cite(
    *, hydrated: HydratedEvidencePool,
) -> GateOutcome:
    """G6 CITE — Do spans resolve to stable anchors?"""
    bad: list[str] = []
    for h in hydrated.hydrated:
        if not h.quality.citation_anchor_stable or not h.citation_anchor_candidates:
            bad.append(h.candidate.chunk_id)
    if not bad:
        return GateOutcome(C0Gate.G6_CITE, True, "all chunks have stable citation anchors")
    if len(bad) == len(hydrated.hydrated):
        return GateOutcome(
            C0Gate.G6_CITE, False,
            "no chunk has a stable citation anchor",
            severity="block", affected_chunk_ids=tuple(bad),
        )
    return GateOutcome(
        C0Gate.G6_CITE, False,
        f"{len(bad)}/{len(hydrated.hydrated)} chunks lack stable anchors",
        severity="warn", affected_chunk_ids=tuple(bad),
    )


def G7_conflict(
    *, conflict: ConflictGapReport,
) -> GateOutcome:
    """G7 CONFLICT — Are contradictions surfaced?

    The gate ALWAYS passes if contradictions are recorded (surfacing them is
    the contract). It only fails if the report claims zero conflicts BUT the
    contradiction set is suspicious (no-op — caller's job to detect).
    """
    return GateOutcome(
        C0Gate.G7_CONFLICT, True,
        f"{len(conflict.contradictions)} contradiction(s) surfaced; "
        f"{len(conflict.gaps)} gap(s) recorded",
    )


def G8_cover(
    *, contract: EvidenceContract, min_direct: float = 0.40,
) -> GateOutcome:
    """G8 COVER — Does evidence cover the full support target?"""
    direct = contract.score_breakdown.direct_support_score
    if direct >= min_direct:
        return GateOutcome(
            C0Gate.G8_COVER, True,
            f"direct_support={direct:.2f} >= {min_direct}",
        )
    return GateOutcome(
        C0Gate.G8_COVER, False,
        f"direct_support={direct:.2f} below {min_direct} — coverage weak",
        severity="warn",
    )


def G9_budget(
    *, shaped: ShapedEvidenceSet, max_token_context: int,
) -> GateOutcome:
    """G9 BUDGET — Can context fit without losing must-use evidence?"""
    must_use_tokens = sum(
        len(r.chunk.candidate.text) // 4 for r in shaped.must_use
    )
    if must_use_tokens <= max_token_context:
        return GateOutcome(
            C0Gate.G9_BUDGET, True,
            f"must_use ~{must_use_tokens} tokens fits in budget {max_token_context}",
        )
    return GateOutcome(
        C0Gate.G9_BUDGET, False,
        f"must_use ~{must_use_tokens} tokens exceeds budget {max_token_context}",
        severity="warn",
    )


def G10_inject(
    *, plan: L1PlanContract, candidates: CandidateEvidencePool | None = None,
) -> GateOutcome:
    """G10 INJECT — Is retrieved text safely classified as data?

    Scans candidate text + user-task text for prompt-injection markers.
    Markers DO NOT block; they quarantine. Caller must move flagged chunks
    to EXCLUDED with reason="instruction_payload_quarantine".
    """
    flagged_ids: list[str] = []
    if candidates is not None:
        for c in candidates.candidates:
            if detect_injection_markers(c.text):
                flagged_ids.append(c.chunk_id)
    user_markers = detect_injection_markers(plan.user_task_text)
    if not flagged_ids and not user_markers:
        return GateOutcome(C0Gate.G10_INJECT, True, "no injection markers detected")
    parts: list[str] = []
    if flagged_ids:
        parts.append(f"{len(flagged_ids)} chunk(s) flagged for instruction-like text")
    if user_markers:
        parts.append(f"user task carries injection markers: {','.join(user_markers)}")
    return GateOutcome(
        C0Gate.G10_INJECT, False,
        "; ".join(parts),
        severity="warn", affected_chunk_ids=tuple(flagged_ids),
    )


# ----- aggregate runner -----


def run_all_gates(
    *,
    route: RouteContract,
    plan_contract: L1PlanContract,
    preflight: C0PreflightStatus,
    plan: RetrievalPlan,
    candidates: CandidateEvidencePool,
    hydrated: HydratedEvidencePool,
    expanded: GraphExpandedEvidencePool,
    shaped: ShapedEvidenceSet,
    conflict: ConflictGapReport,
    contract: EvidenceContract,
) -> GateReport:
    """Run every gate G0..G10 in pipeline order.

    The dispatcher uses the resulting GateReport to:
      - drive the FinalEvidenceContract.status (any block-severity fail =>
        BLOCKED unless higher-priority status applies)
      - populate blocked_reason with the first block outcome
      - extend excluded_with_reasons with affected_chunk_ids
    """
    outcomes = (
        G0_scope(route=route, plan=plan_contract, preflight=preflight),
        G1_acl(hydrated=hydrated, route=route),
        G2_fresh(hydrated=hydrated, route=route),
        G3_exact(plan=plan, hydrated=hydrated),
        G4_dense(hydrated=hydrated),
        G5_graph(expanded=expanded, max_hops=plan.graph_bounds.max_hops),
        G6_cite(hydrated=hydrated),
        G7_conflict(conflict=conflict),
        G8_cover(contract=contract),
        G9_budget(shaped=shaped, max_token_context=plan.budgets.max_token_context),
        G10_inject(plan=plan_contract, candidates=candidates),
    )
    return GateReport(plan_id=plan.plan_id, outcomes=outcomes)


__all__ = [
    "GateOutcome",
    "GateReport",
    "G0_scope",
    "G1_acl",
    "G2_fresh",
    "G3_exact",
    "G4_dense",
    "G5_graph",
    "G6_cite",
    "G7_conflict",
    "G8_cover",
    "G9_budget",
    "G10_inject",
    "run_all_gates",
]
