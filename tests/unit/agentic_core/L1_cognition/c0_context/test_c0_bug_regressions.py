"""Regression tests for C0 Context Engine bugs found and fixed 2026-04-26.

Each test class targets one fixed bug and asserts the *correct* (post-fix)
behavior. The docstring on each test names the bug, what was wrong, and why
the new behavior is right per spec.

If any of these tests start failing, the corresponding bug has regressed.
"""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.c0_context.contract import (
    build_final_contract,
    contract_digest,
    decide_status,
    score,
)
from agentic_core.L1_cognition.c0_context.preflight import preflight
from agentic_core.L1_cognition.c0_context.shape_and_scan import (
    scan_contradictions_and_gaps,
    stratify,
)
from agentic_core.L1_cognition.c0_context.types import (
    ContradictionFlag,
    ContradictionType,
    EvidenceClass,
    EvidenceItem,
    FinalEvidenceContract,
    GapType,
    RecommendedDisposition,
    RouteContractView,
    ScoreBreakdown,
    SupportStatus,
    SupportTarget,
)


# ---------------------------------------------------------------------------
# Test fixtures (kept local to this file to avoid coupling to other tests).
# ---------------------------------------------------------------------------


def _evidence(
    *,
    eid: str = "e1",
    source: str = "doc:a",
    source_class: str = "docs",
    span: str = "L10",
    lane: str = "dense",
    acl: str = "cleared",
    cls: EvidenceClass = EvidenceClass.SUPPORTING,
    authority: float = 0.6,
    fresh: str = "fresh",
    cost: int = 10,
) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=eid,
        source_id=source,
        source_class=source_class,
        span_ref=span,
        quote_or_summary="...",
        retrieval_lane=lane,
        authority_score=authority,
        freshness_status=fresh,
        acl_status=acl,
        token_cost=cost,
        evidence_class=cls,
    )


def _route(**overrides) -> RouteContractView:
    base = dict(
        route_id="R3_GROUNDED",
        grounding_required=True,
        execution_form="read",
        freshness_class="static",
        support_target=SupportTarget.SOURCE_SUMMARY,
        tenant_scope="tenantA",
        acl=("default",),
        region="us",
        data_class="open",
        max_k=20,
        max_hops=3,
        max_parent_expansion=2,
        max_refine_attempts=1,
        max_latency_ms=2000,
        token_budget=4096,
        allowed_sources=frozenset({"docs", "code"}),
        disallowed_sources=frozenset(),
        fallback_policy="R5",
        route_replay_key="rk-1",
        policy_hash="ph-1",
        blueprint_hash="bh-1",
    )
    base.update(overrides)
    return RouteContractView(**base)


# ===========================================================================
# Bug 1 — _has_exact_quote rejected metadata lane (shape_and_scan.py)
# ===========================================================================


class TestBug1MetadataLaneAcceptedAsExactQuote:
    """Bug 1: ``_has_exact_quote`` accepted only ``{sparse, hybrid}`` but the
    spec (and ``i5_exact_claims_need_sparse_or_metadata`` + ``exactness_score``
    in contract.py) all include ``metadata``. Items retrieved via metadata lane
    were wrongly triggering MISSING_EXACT_QUOTE gap.
    """

    def test_metadata_lane_with_span_satisfies_exact_quote(self) -> None:
        """A metadata-lane item with a stable span_ref MUST satisfy an
        EXACT_QUOTE target — no MISSING_EXACT_QUOTE gap should fire."""
        item = _evidence(
            eid="m1",
            lane="metadata",
            cls=EvidenceClass.MUST_USE,
            authority=0.95,
        )
        shaped = stratify([item])
        report = scan_contradictions_and_gaps(
            shaped,
            support_target=SupportTarget.EXACT_QUOTE,
            high_stakes=False,
        )
        gap_types = {g.gap_type for g in report.unresolved_gaps}
        assert GapType.MISSING_EXACT_QUOTE not in gap_types, (
            "metadata-lane item with span_ref must satisfy EXACT_QUOTE; "
            f"got gaps: {gap_types}"
        )

    def test_dense_lane_only_still_emits_missing_exact_quote(self) -> None:
        """Sanity: the fix did NOT loosen dense-only enforcement. Dense lane
        alone for an EXACT_QUOTE target STILL emits MISSING_EXACT_QUOTE."""
        item = _evidence(
            eid="d1",
            lane="dense",
            cls=EvidenceClass.MUST_USE,
            authority=0.95,
        )
        shaped = stratify([item])
        report = scan_contradictions_and_gaps(
            shaped,
            support_target=SupportTarget.EXACT_QUOTE,
            high_stakes=False,
        )
        gap_types = {g.gap_type for g in report.unresolved_gaps}
        assert GapType.MISSING_EXACT_QUOTE in gap_types

    def test_metadata_lane_consistent_with_exactness_score(self) -> None:
        """Cross-module consistency: metadata lane should both (a) avoid
        MISSING_EXACT_QUOTE gap AND (b) count toward exactness_score
        (>0). Before the fix, only (b) was true — that inconsistency was
        the bug."""
        item = _evidence(
            eid="m1",
            lane="metadata",
            cls=EvidenceClass.MUST_USE,
            authority=0.95,
        )
        shaped = stratify([item])
        report = scan_contradictions_and_gaps(
            shaped,
            support_target=SupportTarget.EXACT_QUOTE,
            high_stakes=False,
        )
        breakdown = score(shaped, report, support_target=SupportTarget.EXACT_QUOTE)
        # exactness_score must be > 0 (metadata is a valid exact-quote lane).
        assert breakdown.exactness_score > 0.0
        # AND no MISSING_EXACT_QUOTE gap.
        assert not any(
            g.gap_type is GapType.MISSING_EXACT_QUOTE for g in report.unresolved_gaps
        )


# ===========================================================================
# Bug 2 — contract_digest included nondeterministic contract_id (uuid)
# ===========================================================================


class TestBug2ContractDigestIsContentAddressed:
    """Bug 2: ``build_final_contract`` mints a fresh ``uuid.uuid4()`` for
    ``contract_id`` on every call. The digest used to include that uuid,
    so two calls with identical inputs produced different digests — defeating
    the C0.5 "replay-cert" intent.

    Pre-existing test ``test_replay_determinism_across_full_C0_stage``
    only worked because it manually rewrote contract_id to a fixed string
    before calling ``contract_digest``. That workaround masked the bug for
    all other callers.
    """

    def _build_identical_inputs(self) -> tuple[FinalEvidenceContract, FinalEvidenceContract]:
        """Build two contracts via the public API with identical inputs.
        With the bug, contract_ids differ → digests differ.
        With the fix, digests must be identical because contract_id is
        excluded from the payload."""
        items = [
            _evidence(eid="m", source="doc:1", authority=0.95, cls=EvidenceClass.MUST_USE, lane="sparse"),
        ]
        shaped = stratify(items)
        report = scan_contradictions_and_gaps(
            shaped, support_target=SupportTarget.SOURCE_SUMMARY, high_stakes=False,
        )
        breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
        c1 = build_final_contract(
            route=_route(), shaped=shaped, report=report, breakdown=breakdown,
        )
        c2 = build_final_contract(
            route=_route(), shaped=shaped, report=report, breakdown=breakdown,
        )
        return c1, c2

    def test_digest_replay_stable_across_independent_build_calls(self) -> None:
        """Two independent ``build_final_contract`` calls with identical
        inputs MUST produce identical digests. (Bug 2 — fixed.)"""
        c1, c2 = self._build_identical_inputs()
        # Sanity: contract_ids ARE different (proves the uuid is fresh).
        assert c1.contract_id != c2.contract_id
        # Fix: digests are identical despite different contract_ids.
        assert contract_digest(c1) == contract_digest(c2), (
            "contract_digest must be content-addressed, not name-addressed; "
            "fresh uuid contract_id must NOT alter the digest"
        )

    def test_digest_does_not_depend_on_contract_id(self) -> None:
        """Direct probe: cloning a contract with a different contract_id
        must yield the same digest."""
        c1, _ = self._build_identical_inputs()
        c_renamed = FinalEvidenceContract(
            contract_id="totally-different-id",
            route_id=c1.route_id,
            route_replay_key=c1.route_replay_key,
            policy_hash=c1.policy_hash,
            blueprint_hash=c1.blueprint_hash,
            status=c1.status,
            support_score=c1.support_score,
            score_breakdown=c1.score_breakdown,
            evidence=c1.evidence,
            contradiction_flags=c1.contradiction_flags,
            unresolved_gaps=c1.unresolved_gaps,
            recommended_disposition=c1.recommended_disposition,
            refine_attempts=c1.refine_attempts,
            extras=c1.extras,
        )
        assert contract_digest(c1) == contract_digest(c_renamed)


# ===========================================================================
# Bug 3 — contract_digest collided across different evidence pools
# ===========================================================================


class TestBug3DigestDistinguishesEvidencePools:
    """Bug 3: the old digest payload only carried aggregate counts
    (n_evidence, n_contradictions, n_gaps) plus status + support_score.
    Two contracts with completely different evidence content but the same
    counts and score collapsed to the same digest — useless as audit proof.
    """

    def _build_with_evidence(self, sources: list[str]) -> FinalEvidenceContract:
        items = [
            _evidence(
                eid=f"e{i}",
                source=src,
                authority=0.95,
                cls=EvidenceClass.MUST_USE,
                lane="sparse",
            )
            for i, src in enumerate(sources)
        ]
        shaped = stratify(items)
        report = scan_contradictions_and_gaps(
            shaped, support_target=SupportTarget.SOURCE_SUMMARY, high_stakes=False,
        )
        breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
        return build_final_contract(
            route=_route(), shaped=shaped, report=report, breakdown=breakdown,
        )

    def test_different_sources_produce_different_digests(self) -> None:
        """Two contracts with the same counts/status/score but different
        evidence sources MUST produce different digests."""
        c_a = self._build_with_evidence(["doc:alpha", "doc:beta", "doc:gamma"])
        c_b = self._build_with_evidence(["doc:x", "doc:y", "doc:z"])
        # Both have 3 must_use items, identical score breakdown shape, same
        # status, no contradictions, no gaps.
        assert c_a.status == c_b.status
        assert len(c_a.evidence) == len(c_b.evidence)
        assert len(c_a.contradiction_flags) == len(c_b.contradiction_flags)
        assert len(c_a.unresolved_gaps) == len(c_b.unresolved_gaps)
        # Bug 3 fix: digests differ because evidence content is hashed.
        assert contract_digest(c_a) != contract_digest(c_b), (
            "different evidence pools must produce different digests"
        )

    def test_different_evidence_ids_produce_different_digests(self) -> None:
        """Even with identical source_ids, different ``evidence_id`` values
        must yield different digests (replay-cert must distinguish them)."""
        items_a = [
            _evidence(eid="a1", source="doc:1", authority=0.95, cls=EvidenceClass.MUST_USE, lane="sparse"),
        ]
        items_b = [
            _evidence(eid="b1", source="doc:1", authority=0.95, cls=EvidenceClass.MUST_USE, lane="sparse"),
        ]
        shaped_a = stratify(items_a)
        shaped_b = stratify(items_b)
        rep_a = scan_contradictions_and_gaps(shaped_a, support_target=SupportTarget.SOURCE_SUMMARY, high_stakes=False)
        rep_b = scan_contradictions_and_gaps(shaped_b, support_target=SupportTarget.SOURCE_SUMMARY, high_stakes=False)
        bd_a = score(shaped_a, rep_a, support_target=SupportTarget.SOURCE_SUMMARY)
        bd_b = score(shaped_b, rep_b, support_target=SupportTarget.SOURCE_SUMMARY)
        c_a = build_final_contract(route=_route(), shaped=shaped_a, report=rep_a, breakdown=bd_a)
        c_b = build_final_contract(route=_route(), shaped=shaped_b, report=rep_b, breakdown=bd_b)
        assert contract_digest(c_a) != contract_digest(c_b)


# ===========================================================================
# Bug 4 — decide_status returned EMPTY when only CONTRADICTS items present,
#         hiding contradictions in violation of invariant I7.
# ===========================================================================


class TestBug4ContradictionsSurfacedEvenWithoutAnchor:
    """Bug 4: ``decide_status`` checked ``has_evidence = bool(must_use or
    supporting)`` BEFORE checking contradiction_flags. A pool of pure
    CONTRADICTS items (no must_use/supporting) returned EMPTY → ABSTAIN,
    silently swallowing the contradictions.

    This violates invariant **I7** ("contradictions must be surfaced, not
    hidden"). After the fix, credible contradictions take priority over
    EMPTY.
    """

    def test_only_contradicts_with_high_severity_yields_conflicted_not_empty(self) -> None:
        """Pool with only a CONTRADICTS item at severity ≥ 0.6 must report
        CONFLICTED, not EMPTY."""
        contra = _evidence(
            eid="c1",
            source="doc:contra",
            authority=0.9,  # → contradiction severity 0.9, ≥ 0.6 threshold
            cls=EvidenceClass.CONTRADICTS,
        )
        shaped = stratify([contra])
        # Sanity — confirm pool truly has no must_use/supporting.
        assert shaped.must_use == ()
        assert shaped.supporting == ()
        assert shaped.contradicts != ()
        report = scan_contradictions_and_gaps(
            shaped, support_target=SupportTarget.SOURCE_SUMMARY, high_stakes=False,
        )
        # Sanity — scan emits a contradiction flag even without anchor.
        assert len(report.contradiction_flags) == 1
        assert report.contradiction_flags[0].severity >= 0.6
        breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
        status = decide_status(shaped, report, breakdown)
        assert status is SupportStatus.CONFLICTED, (
            "I7: a credible contradiction must surface as CONFLICTED, "
            f"not be hidden as EMPTY; got {status}"
        )

    def test_empty_pool_with_no_contradictions_still_returns_empty(self) -> None:
        """Sanity: the fix did not change EMPTY behavior for truly empty pools."""
        shaped = stratify([])
        report = scan_contradictions_and_gaps(
            shaped, support_target=SupportTarget.SOURCE_SUMMARY, high_stakes=False,
        )
        breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
        assert decide_status(shaped, report, breakdown) is SupportStatus.EMPTY

    def test_blocked_still_overrides_contradictions(self) -> None:
        """Sanity: BLOCKED still wins over CONFLICTED when both are
        applicable (BLOCKED ≻ CONFLICTED ≻ EMPTY)."""
        contra = _evidence(
            eid="c1",
            source="doc:contra",
            authority=0.9,
            cls=EvidenceClass.CONTRADICTS,
        )
        shaped = stratify([contra])
        report = scan_contradictions_and_gaps(
            shaped, support_target=SupportTarget.SOURCE_SUMMARY, high_stakes=False,
        )
        breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
        assert decide_status(shaped, report, breakdown, blocked=True) is SupportStatus.BLOCKED

    def test_low_severity_contradictions_alone_still_yield_empty(self) -> None:
        """Edge case: a CONTRADICTS item with authority < 0.6 produces a
        contradiction flag with severity < 0.6, which does NOT meet the
        CONFLICTED bar. Pool with no must_use → still EMPTY (low-severity
        contradictions surface via the gap/contradiction-risk mechanism,
        not via status)."""
        weak_contra = _evidence(
            eid="c1",
            source="doc:contra",
            authority=0.3,  # severity 0.3 < 0.6 threshold
            cls=EvidenceClass.CONTRADICTS,
        )
        shaped = stratify([weak_contra])
        report = scan_contradictions_and_gaps(
            shaped, support_target=SupportTarget.SOURCE_SUMMARY, high_stakes=False,
        )
        breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
        # Spec choice: low-severity contradictions don't trip CONFLICTED.
        # With no must_use/supporting, the result is EMPTY (downstream sees
        # contradiction_risk in the score breakdown).
        assert decide_status(shaped, report, breakdown) is SupportStatus.EMPTY


# ===========================================================================
# Bug 5 — Dead code in score(): exactness_score = exactness_score * 1.0
# ===========================================================================


class TestBug5NoDeadMultiplierInScore:
    """Bug 5: ``score()`` had ``exactness_score = exactness_score * 1.0``
    inside an ``if support_target in {EXACT_QUOTE, POLICY_CLAUSE,
    CODE_LOCATION}`` branch — a no-op multiplication. The branch had no
    behavioral effect; either it was dead code or a missing feature. We
    chose to delete it: spec strictness for those targets is enforced
    upstream by ``scan_contradictions_and_gaps`` (MISSING_EXACT_QUOTE gap
    fires when sparse/metadata/hybrid is absent), which feeds
    unsupported_inference_risk and decide_status.
    """

    def test_exactness_score_identical_across_high_and_low_strict_targets(self) -> None:
        """The dead branch made `exactness_score` numerically identical
        between high-strict and low-strict targets. After deletion, the
        invariant still holds (because the upstream gap mechanism is what
        enforces strictness, not a multiplier here)."""
        # Same item, same lane mix — only support_target differs.
        item = _evidence(
            eid="a",
            lane="sparse",
            cls=EvidenceClass.MUST_USE,
            authority=0.95,
        )
        shaped = stratify([item])
        report = scan_contradictions_and_gaps(
            shaped, support_target=SupportTarget.SOURCE_SUMMARY, high_stakes=False,
        )

        bd_strict = score(shaped, report, support_target=SupportTarget.POLICY_CLAUSE)
        bd_loose = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)

        # exactness_score (the dimension touched by the dead code) must be
        # identical because the deleted branch was a no-op.
        assert bd_strict.exactness_score == bd_loose.exactness_score

    def test_score_is_pure_in_support_target_for_exactness_dimension(self) -> None:
        """exactness_score depends only on lane mix, not on support_target.
        (If the spec ever wants per-target strictness, a non-trivial
        multiplier should be added — at which point this test will fail
        and force a deliberate spec-aligned change.)"""
        item = _evidence(
            eid="a", lane="sparse", cls=EvidenceClass.MUST_USE, authority=0.95
        )
        shaped = stratify([item])
        report = scan_contradictions_and_gaps(
            shaped, support_target=SupportTarget.SOURCE_SUMMARY, high_stakes=False
        )
        scores_by_target = {
            t: score(shaped, report, support_target=t).exactness_score
            for t in [
                SupportTarget.SOURCE_SUMMARY,
                SupportTarget.EXACT_QUOTE,
                SupportTarget.POLICY_CLAUSE,
                SupportTarget.CODE_LOCATION,
                SupportTarget.INCIDENT_EVIDENCE,
                SupportTarget.ROOT_CAUSE_RANKING,
                SupportTarget.COMPARISON,
                SupportTarget.CLAIM_CHECK,
            ]
        }
        unique_values = set(scores_by_target.values())
        assert len(unique_values) == 1, (
            f"exactness_score should not differ across support_target after "
            f"dead-code removal; got {scores_by_target}"
        )
