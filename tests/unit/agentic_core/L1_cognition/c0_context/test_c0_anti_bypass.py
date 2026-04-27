"""C0.7 anti-bypass / negative-gate / failure-mode preventive tests.

Doctrine: ``docs/reference/03A_C0_Context_Engine/C0.7_C0_Observability_Tests_Anti_Bypass.md``

C0.7 PHASE 4 enumerates **30 mandatory named tests**:
  - 11 per-gate negative tests (C0.G0..C0.G10)
  - 14 per-failure-mode preventive tests
  - 5 stage-spanning anti-bypass tests

Each test name below matches the exact spelling prescribed by the spec so that
any spec audit can grep the codebase and confirm coverage. The assertions wire
through the real implementation surface in
``agentic_core/L1_cognition/c0_context/`` — no mocks of the gates themselves.
"""

from __future__ import annotations

import inspect
import pkgutil
from pathlib import Path

import pytest

from agentic_core.L1_cognition import c0_context as c0_pkg
from agentic_core.L1_cognition.c0_context import contract as c0_contract
from agentic_core.L1_cognition.c0_context import preflight as c0_preflight
from agentic_core.L1_cognition.c0_context import refine as c0_refine
from agentic_core.L1_cognition.c0_context import safety as c0_safety
from agentic_core.L1_cognition.c0_context import shape_and_scan as c0_shape
from agentic_core.L1_cognition.c0_context import types as c0_types
from agentic_core.L1_cognition.c0_context.contract import (
    build_final_contract,
    contract_digest,
    decide_status,
    score,
    verify_evidence,
)
from agentic_core.L1_cognition.c0_context.preflight import (
    MIN_BUDGET_FLOOR_TOKENS,
    build_retrieval_plan,
    preflight,
)
from agentic_core.L1_cognition.c0_context.refine import (
    DisallowedRefinementError,
    RefineLoopController,
    RefinementAttempt,
    RefinementBudgetExhaustedError,
)
from agentic_core.L1_cognition.c0_context.safety import (
    InvariantViolationError,
    assert_all_invariants,
    gate_g0_scope,
    gate_g1_acl,
    gate_g2_fresh,
    gate_g3_exact,
    gate_g4_dense,
    gate_g5_graph,
    gate_g6_cite,
    gate_g7_conflict,
    gate_g8_cover,
    gate_g9_budget,
    gate_g10_inject,
    i2_retrieved_data_not_instruction,
    i3_lineage_preserved,
    i6_graph_bounded,
    i7_contradictions_surfaced,
    i8_weak_evidence_stays_weak,
)
from agentic_core.L1_cognition.c0_context.shape_and_scan import (
    compress_to_budget,
    dedupe,
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
    RefineTactic,
    RouteContractView,
    ScoreBreakdown,
    SupportStatus,
    SupportTarget,
)


# ---------------------------------------------------------------------------
# Shared fixtures / helpers.
# ---------------------------------------------------------------------------


def _evidence(
    *,
    eid: str = "e1",
    source: str = "doc:a",
    source_class: str = "docs",
    span: str = "L10",
    lane: str = "dense",
    acl: str = "cleared",
    cls: EvidenceClass = EvidenceClass.MUST_USE,
    authority: float = 0.9,
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


def _route(
    *,
    grounding: bool = True,
    route_id: str = "R3_GROUNDED",
    tenant: str = "tenantA",
    acl: tuple[str, ...] = ("default",),
    region: str = "us",
    data_class: str = "open",
    allowed: frozenset[str] = frozenset({"docs", "code"}),
    disallowed: frozenset[str] = frozenset(),
    support_target: SupportTarget = SupportTarget.SOURCE_SUMMARY,
    token_budget: int = 4096,
    max_hops: int = 3,
    max_k: int = 20,
    max_parent: int = 2,
    max_refine: int = 1,
    freshness: str = "static",
) -> RouteContractView:
    return RouteContractView(
        route_id=route_id,
        grounding_required=grounding,
        execution_form="read",
        freshness_class=freshness,
        support_target=support_target,
        tenant_scope=tenant,
        acl=acl,
        region=region,
        data_class=data_class,
        max_k=max_k,
        max_hops=max_hops,
        max_parent_expansion=max_parent,
        max_refine_attempts=max_refine,
        max_latency_ms=2000,
        token_budget=token_budget,
        allowed_sources=allowed,
        disallowed_sources=disallowed,
        fallback_policy="R5",
        route_replay_key="rk-1",
        policy_hash="ph-1",
        blueprint_hash="bh-1",
    )


def _contract(
    *,
    status: SupportStatus = SupportStatus.PASS,
    score_value: float = 0.9,
    evidence: tuple[EvidenceItem, ...] = (),
    flags: tuple[ContradictionFlag, ...] = (),
    refine_attempts: int = 0,
    extras: dict[str, str] | None = None,
    disposition: RecommendedDisposition = RecommendedDisposition.PROCEED,
) -> FinalEvidenceContract:
    return FinalEvidenceContract(
        contract_id="c1",
        route_id="R3_GROUNDED",
        route_replay_key="rk-1",
        policy_hash="ph-1",
        blueprint_hash="bh-1",
        status=status,
        support_score=score_value,
        score_breakdown=ScoreBreakdown(),
        evidence=evidence,
        contradiction_flags=flags,
        unresolved_gaps=(),
        recommended_disposition=disposition,
        refine_attempts=refine_attempts,
        extras=extras if extras is not None else {"content_classification": "data"},
    )


# ===========================================================================
# PHASE 4 — PER-GATE NEGATIVE TESTS (C0.G0..C0.G10) — 11 tests.
# ===========================================================================


def test_c0_g0_scope_blocked_when_route_disallows_grounding() -> None:
    """C0.G0 Scope — preflight blocks when grounding_required is False."""
    route = _route(grounding=False)
    status = preflight(route)
    assert status.eligible is False
    assert status.blocked_reason == "grounding_not_required"
    # Gate predicate agrees.
    assert gate_g0_scope(route_allows_retrieval=False).passed is False


def test_c0_g1_acl_blocks_wrong_tenant_evidence() -> None:
    """C0.G1 ACL — evidence with non-cleared ACL is rejected by verify_evidence."""
    good = _evidence(eid="ok", acl="cleared")
    bad = _evidence(eid="bad", acl="blocked-tenantB", source="doc:leak")
    verified, rejected = verify_evidence((good, bad))
    assert len(verified) == 1
    assert verified[0].evidence_id == "ok"
    assert any("acl_status" in reason for _it, reason in rejected)
    # Gate predicate.
    assert gate_g1_acl(all_sources_acl_cleared=False).passed is False


def test_c0_g2_freshness_marks_stale_source_or_excludes() -> None:
    """C0.G2 Fresh — stale evidence lowers freshness score; gate fails."""
    outcome = gate_g2_fresh(freshness_satisfied=False)
    assert outcome.passed is False
    assert "stale" in outcome.reason.lower()
    # End-to-end: stale items reduce score below PASS threshold.
    stale_items = [
        _evidence(eid=f"e{i}", source=f"doc:{i}", fresh="stale", authority=0.9, lane="sparse")
        for i in range(3)
    ]
    shaped = stratify(stale_items)
    report = scan_contradictions_and_gaps(
        shaped,
        support_target=SupportTarget.SOURCE_SUMMARY,
        high_stakes=False,
    )
    breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
    # Stale → freshness_score should be 0.5 (per contract.py mapping).
    assert breakdown.freshness_score <= 0.5


def test_c0_g3_exact_requires_sparse_or_metadata_support() -> None:
    """C0.G3 Exact — exact claim with no sparse/metadata support fails the gate."""
    outcome = gate_g3_exact(has_exact_claim=True, sparse_or_metadata_present=False)
    assert outcome.passed is False
    # Scan surfaces the missing-exact-quote gap.
    dense_only = [_evidence(eid="a", lane="dense", authority=0.9)]
    shaped = stratify(dense_only)
    report = scan_contradictions_and_gaps(
        shaped,
        support_target=SupportTarget.EXACT_QUOTE,
        high_stakes=False,
    )
    assert any(g.gap_type == GapType.MISSING_EXACT_QUOTE for g in report.unresolved_gaps)


def test_c0_g4_dense_only_weak_hit_is_pruned() -> None:
    """C0.G4 Dense — low-relevance dense hits are pruned by stratify() into EXCLUDED."""
    # authority below background threshold (0.25) → excluded.
    # Use SUPPORTING as the starting class so authority-based re-stratification runs
    # (pre-labeled MUST_USE items bypass the threshold logic by spec).
    weak_item = _evidence(eid="weak", authority=0.10, cls=EvidenceClass.SUPPORTING)
    strong_item = _evidence(eid="strong", authority=0.95, cls=EvidenceClass.SUPPORTING)
    shaped = stratify([weak_item, strong_item])
    excluded_ids = {it.evidence_id for it, _r in shaped.excluded}
    assert "weak" in excluded_ids
    assert "strong" not in excluded_ids
    # Gate predicate.
    assert gate_g4_dense(dense_relevance_score=0.10).passed is False


def test_c0_g5_graph_traversal_stops_at_max_hops() -> None:
    """C0.G5 Graph — graph hops exceeding max_hops fail both invariant and gate."""
    assert i6_graph_bounded(hops_used=5, max_hops=3) is False
    outcome = gate_g5_graph(hops_used=5, max_hops=3)
    assert outcome.passed is False
    assert "hops" in outcome.reason.lower()


def test_c0_g6_cite_unstable_span_is_excluded_or_downgraded() -> None:
    """C0.G6 Cite — evidence with unresolved span_ref is rejected by verify_evidence."""
    no_span = _evidence(eid="nospan", span="")
    has_span = _evidence(eid="hasspan", span="L10")
    verified, rejected = verify_evidence((no_span, has_span))
    assert {it.evidence_id for it in verified} == {"hasspan"}
    assert any("span_ref_missing" in reason for _it, reason in rejected)
    assert gate_g6_cite(all_anchors_resolve=False).passed is False


def test_c0_g7_conflict_contradiction_surfaces_as_CONTRADICTS() -> None:
    """C0.G7 Conflict — CONTRADICTS items produce ContradictionFlag, not silent drop."""
    anchor = _evidence(eid="a", cls=EvidenceClass.MUST_USE, authority=0.9)
    contra = _evidence(
        eid="c",
        cls=EvidenceClass.CONTRADICTS,
        source="doc:other",
        authority=0.8,
    )
    shaped = stratify([anchor, contra])
    report = scan_contradictions_and_gaps(
        shaped,
        support_target=SupportTarget.SOURCE_SUMMARY,
        high_stakes=False,
    )
    assert len(report.contradiction_flags) == 1
    assert report.contradiction_flags[0].source_a == "doc:other"
    # And the gate fails when contradictions are present but not surfaced.
    assert gate_g7_conflict(contradictions_surfaced=False).passed is False


def test_c0_g8_cover_partial_target_marks_WEAK_or_refines() -> None:
    """C0.G8 Cover — partial coverage leads to WEAK / WEAK_WITH_CAVEATS, never PASS."""
    # Only one supporting item — no MUST_USE → coverage low.
    items = [_evidence(eid="a", authority=0.55)]
    shaped = stratify(items)
    report = scan_contradictions_and_gaps(
        shaped,
        support_target=SupportTarget.SOURCE_SUMMARY,
        high_stakes=False,
    )
    breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
    status = decide_status(shaped, report, breakdown)
    assert status in {SupportStatus.WEAK, SupportStatus.WEAK_WITH_CAVEATS}
    assert gate_g8_cover(coverage_score=0.10).passed is False


def test_c0_g9_budget_trim_preserves_must_use_evidence() -> None:
    """C0.G9 Budget — compress_to_budget trims BACKGROUND first; never MUST_USE."""
    must = _evidence(eid="m", cls=EvidenceClass.MUST_USE, authority=0.95, cost=30)
    supp = _evidence(eid="s", cls=EvidenceClass.SUPPORTING, authority=0.6, cost=20)
    bg = _evidence(eid="b", cls=EvidenceClass.BACKGROUND, authority=0.3, cost=40)
    shaped = stratify([must, supp, bg])
    compressed = compress_to_budget(shaped, max_token_context=50)
    # Must-use preserved.
    assert {it.evidence_id for it in compressed.must_use} == {"m"}
    # Background trimmed (40 tokens won't fit after 30 must + 20 supporting = 50).
    assert len(compressed.background) == 0
    assert gate_g9_budget(must_use_fits_budget=True).passed is True
    assert gate_g9_budget(must_use_fits_budget=False).passed is False


def test_c0_g10_inject_instruction_like_payload_is_quarantined() -> None:
    """C0.G10 Inject — retrieved text flagged as instruction fails invariant + gate."""
    # I2 — content must be classified as "data".
    assert i2_retrieved_data_not_instruction({"content_classification": "instruction"}) is False
    assert i2_retrieved_data_not_instruction({"content_classification": "data"}) is True
    # Gate.
    assert gate_g10_inject(retrieved_text_classified_data=False).passed is False


# ===========================================================================
# PHASE 4 — PER-FAILURE-MODE PREVENTIVE TESTS — 14 tests.
# ===========================================================================


def test_no_dense_only_answer_when_exactness_required() -> None:
    """dense_only_hallucination — I5 blocks exact claims backed only by dense lane."""
    from agentic_core.L1_cognition.c0_context.safety import (
        i4_dense_alone_not_enough_for_high_stakes,
        i5_exact_claims_need_sparse_or_metadata,
    )

    assert (
        i5_exact_claims_need_sparse_or_metadata(
            has_exact_claim=True,
            retrieval_lanes_used=frozenset({"dense"}),
        )
        is False
    )
    assert (
        i5_exact_claims_need_sparse_or_metadata(
            has_exact_claim=True,
            retrieval_lanes_used=frozenset({"dense", "sparse"}),
        )
        is True
    )
    assert (
        i4_dense_alone_not_enough_for_high_stakes(
            high_stakes=True,
            retrieval_lanes_used=frozenset({"dense"}),
        )
        is False
    )


def test_no_wrong_tenant_evidence_in_pool() -> None:
    """wrong_tenant_evidence — verify_evidence excludes non-cleared ACL."""
    items = (
        _evidence(eid="ok", acl="cleared"),
        _evidence(eid="wrong-tenant", acl="tenantB-blocked"),
    )
    verified, rejected = verify_evidence(items)
    assert {it.evidence_id for it in verified} == {"ok"}
    assert any("acl_status" in r for _it, r in rejected)


def test_no_stale_policy_answer_without_caveat() -> None:
    """stale_policy_answer — stale freshness + POLICY_CLAUSE → never PASS.

    Single-source stale policy evidence must not reach PASS because (a) the
    freshness dimension drops to 0.5 and (b) POLICY_CLAUSE is a high-stakes
    target where single-source coverage triggers a MISSING_SOURCE_DIVERSITY
    gap, pushing the aggregate below the 0.75 PASS threshold.
    """
    stale = [
        _evidence(eid="p0", fresh="stale", authority=0.85, lane="sparse", source="pol:x"),
    ]
    shaped = stratify(stale)
    report = scan_contradictions_and_gaps(
        shaped,
        support_target=SupportTarget.POLICY_CLAUSE,
        high_stakes=True,
    )
    breakdown = score(shaped, report, support_target=SupportTarget.POLICY_CLAUSE)
    status = decide_status(shaped, report, breakdown)
    assert status != SupportStatus.PASS, f"stale policy evidence must not PASS; got {status}"


def test_no_quote_distortion_when_parent_context_dropped() -> None:
    """quote_distortion — verify_evidence rejects items missing span_ref (no parent context)."""
    distorted = _evidence(eid="no-parent", span="")
    verified, rejected = verify_evidence((distorted,))
    assert verified == ()
    assert rejected and rejected[0][1] == "span_ref_missing"


def test_no_hidden_contradiction() -> None:
    """hidden_contradiction — I7 requires CONFLICTED status to carry contradiction_flags."""
    bad = _contract(status=SupportStatus.CONFLICTED, flags=())
    assert i7_contradictions_surfaced(bad) is False
    good = _contract(
        status=SupportStatus.CONFLICTED,
        flags=(
            ContradictionFlag(
                contradiction_type=ContradictionType.SOURCE,
                source_a="a",
                source_b="b",
                severity=0.9,
                summary="conflict",
            ),
        ),
    )
    assert i7_contradictions_surfaced(good) is True


def test_no_graph_scope_creep_beyond_max_hops() -> None:
    """graph_scope_creep — I6 + G5 forbid hops > max_hops."""
    assert i6_graph_bounded(hops_used=10, max_hops=3) is False
    assert gate_g5_graph(hops_used=10, max_hops=3).passed is False


def test_no_cache_poisoning_without_lineage_check() -> None:
    """cache_poisoning — I3 requires source_id + acl + retrieval_lane on every item."""
    no_lane = EvidenceItem(
        evidence_id="x",
        source_id="doc:1",
        source_class="docs",
        span_ref="L1",
        quote_or_summary="...",
        retrieval_lane="",  # lane missing — lineage broken.
        authority_score=0.9,
        freshness_status="fresh",
        acl_status="cleared",
        token_cost=10,
    )
    assert i3_lineage_preserved(no_lane) is False
    good = _evidence(lane="cache")
    assert i3_lineage_preserved(good) is True


def test_no_prompt_injection_via_retrieved_text() -> None:
    """prompt_injection_via_retrieved_text — I2 rejects instruction classification."""
    bad = _contract(extras={"content_classification": "instruction"})
    assert i2_retrieved_data_not_instruction(bad.extras) is False
    # assert_all_invariants raises on I2 violation.
    with pytest.raises(InvariantViolationError, match="C0.I2"):
        assert_all_invariants(bad, retrieval_lanes_used=frozenset({"dense", "sparse"}))


def test_no_fake_confidence_when_support_is_partial() -> None:
    """fake_confidence — I8: WEAK or WEAK_WITH_CAVEATS MUST carry support_score < 0.85."""
    inflated = _contract(status=SupportStatus.WEAK, score_value=0.95)
    assert i8_weak_evidence_stays_weak(inflated) is False
    honest = _contract(status=SupportStatus.WEAK, score_value=0.40)
    assert i8_weak_evidence_stays_weak(honest) is True


def test_no_lost_lineage_in_lineage_manifest() -> None:
    """lost_lineage — every verified item retains source_id + acl_status + retrieval_lane."""
    ok = _evidence(eid="a", source="doc:x", acl="cleared", lane="sparse")
    assert i3_lineage_preserved(ok) is True
    # An item missing any of the three fails.
    missing_source = EvidenceItem(
        evidence_id="b",
        source_id="",
        source_class="docs",
        span_ref="L1",
        quote_or_summary="...",
        retrieval_lane="dense",
        authority_score=0.9,
        freshness_status="fresh",
        acl_status="cleared",
        token_cost=10,
    )
    assert i3_lineage_preserved(missing_source) is False


def test_no_overstuffed_context_drops_must_use() -> None:
    """overstuffed_context — compress_to_budget raises before must-use is dropped."""
    big_must = _evidence(eid="m", cls=EvidenceClass.MUST_USE, authority=0.95, cost=200)
    shaped = stratify([big_must])
    with pytest.raises(ValueError, match="must-keep"):
        compress_to_budget(shaped, max_token_context=50)


def test_no_unsupported_synthesis_marked_as_direct_support() -> None:
    """unsupported_synthesis — score breakdown exposes direct_support vs inference_risk separately."""
    # High-severity gaps drive unsupported_inference_risk; direct_support stays tied to
    # MUST_USE count. The two dimensions must be independent.
    items = [_evidence(eid="a", authority=0.95)]
    shaped = stratify(items)
    report = scan_contradictions_and_gaps(
        shaped,
        support_target=SupportTarget.SOURCE_SUMMARY,
        high_stakes=True,
    )  # high_stakes + single source → source-diversity gap with severity 0.7
    breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
    assert breakdown.direct_support_score > 0.0
    assert breakdown.unsupported_inference_risk > 0.0, (
        "high-severity gap must surface as inference risk, not as direct support"
    )
    # They are truly distinct attributes.
    assert breakdown.direct_support_score != breakdown.unsupported_inference_risk
    # ScoreBreakdown declares 11 named dimensions per spec.
    assert set(breakdown.as_dict().keys()) == set(c0_types.SCORE_DIMENSIONS)


def test_no_silent_docs_vs_code_preference() -> None:
    """docs_vs_code_mismatch — contradiction type inferred as CODE, flag is non-silent."""
    doc_anchor = _evidence(eid="doc", source_class="docs", cls=EvidenceClass.MUST_USE, authority=0.9)
    code_contra = _evidence(
        eid="code",
        source_class="code",
        cls=EvidenceClass.CONTRADICTS,
        source="code:x",
        authority=0.85,
    )
    shaped = stratify([doc_anchor, code_contra])
    report = scan_contradictions_and_gaps(
        shaped,
        support_target=SupportTarget.SOURCE_SUMMARY,
        high_stakes=False,
    )
    assert len(report.contradiction_flags) == 1
    assert report.contradiction_flags[0].contradiction_type == ContradictionType.CODE


def test_no_silent_runtime_vs_design_preference() -> None:
    """runtime_vs_design_mismatch — logs vs docs contradiction inferred as RUNTIME."""
    doc_anchor = _evidence(eid="doc", source_class="docs", cls=EvidenceClass.MUST_USE, authority=0.9)
    log_contra = _evidence(
        eid="log",
        source_class="logs",
        cls=EvidenceClass.CONTRADICTS,
        source="log:x",
        authority=0.8,
    )
    shaped = stratify([doc_anchor, log_contra])
    report = scan_contradictions_and_gaps(
        shaped,
        support_target=SupportTarget.SOURCE_SUMMARY,
        high_stakes=False,
    )
    assert len(report.contradiction_flags) == 1
    assert report.contradiction_flags[0].contradiction_type == ContradictionType.RUNTIME


# ===========================================================================
# PHASE 4 — STAGE-SPANNING ANTI-BYPASS TESTS — 5 tests.
# ===========================================================================


# Forbidden tokens per C0.7 spec — runtime disposition vocabulary that MUST NOT
# appear in any C0 output (these belong to Runtime Gates / Exit Eval, not C0).
_FORBIDDEN_RUNTIME_TOKENS: frozenset[str] = frozenset(
    {
        "ALLOW",
        "DENY",
        "REROUTE_AUTHORIZED",
        "ESCALATE_HITL",
        "COMMIT_REQUEST",
        "BLOCK_COMMIT",
        "ALLOW_FINISH",
        "CLARIFY",
        "SHRINK_SCOPE",
        "RETRY",
        "HEAL",
        "QUARANTINE",
        "REDACT",
        "SAFE_FALLBACK",
        "MARK_DEGRADED",
        "downstream_disposition",
        "approve_execution",
        "approve_output",
        "approve_write",
    }
)


def test_no_runtime_disposition_vocabulary_in_any_C0_output() -> None:
    """C0.7 anti-bypass — RecommendedDisposition MUST NOT reuse runtime-gate vocab.

    C0 recommends only (PROCEED / PROCEED_WITH_CAVEAT / ABSTAIN / FALLBACK_R5 /
    REROUTE / HUMAN_REVIEW). Runtime dispositions like ALLOW / DENY / COMMIT_REQUEST
    belong to Exit Eval and Runtime Gates, not to C0.
    """
    c0_dispositions = {d.value for d in RecommendedDisposition}
    # No exact equality with forbidden tokens.
    assert c0_dispositions.isdisjoint(_FORBIDDEN_RUNTIME_TOKENS)
    # None of the C0 dispositions contains a forbidden uppercase token.
    for token in _FORBIDDEN_RUNTIME_TOKENS:
        if token.isupper():
            assert not any(d == token for d in c0_dispositions), (
                f"runtime token {token!r} leaked into C0 dispositions: {c0_dispositions}"
            )
    # A well-formed contract never produces these values through build_final_contract.
    route = _route()
    empty_shaped = stratify([])
    report = scan_contradictions_and_gaps(
        empty_shaped,
        support_target=SupportTarget.SOURCE_SUMMARY,
        high_stakes=False,
    )
    breakdown = score(empty_shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
    contract = build_final_contract(
        route=route,
        shaped=empty_shaped,
        report=report,
        breakdown=breakdown,
    )
    assert contract.recommended_disposition.value in c0_dispositions


def test_no_durable_L4_write_attempted_from_C0() -> None:
    """C0.7 anti-bypass — C0 package does not import UWG or L4 write modules.

    UWG is the only durable write path; C0 is READ-ONLY. Any import of the
    write gateway from inside ``agentic_core.L1_cognition.c0_context`` is a
    constitutional violation.
    """
    c0_root = Path(c0_pkg.__file__).parent
    forbidden_imports: list[tuple[str, str]] = []
    write_patterns = (
        "write_gateway",
        "universal_write",
        "uwg",
        "L4_state.persist",
        "canonical_store.write",
        "durable_write",
    )
    for py_file in c0_root.glob("*.py"):
        text = py_file.read_text(encoding="utf-8").lower()
        for pat in write_patterns:
            if f"import {pat}" in text or f"from {pat}" in text or f".{pat}" in text:
                forbidden_imports.append((py_file.name, pat))
    assert forbidden_imports == [], f"C0 package leaked L4 write imports: {forbidden_imports}"


def test_no_route_change_emitted_from_C0() -> None:
    """C0.7 anti-bypass — refinement loop rejects rationale containing "change_route".

    C0 may recommend reroute, but cannot self-authorize a route change. The
    refinement loop enforces this via DISALLOWED_REFINEMENTS.
    """
    assert "change_route" in c0_types.DISALLOWED_REFINEMENTS
    route = _route()
    p_status = preflight(route)
    plan = build_retrieval_plan(route, p_status)
    controller = RefineLoopController(plan=plan)
    with pytest.raises(DisallowedRefinementError, match="change_route"):
        controller.request_refinement(
            RefineTactic.REWRITE,
            rationale="we should change_route to R4 because route is wrong",
            current_status=SupportStatus.WEAK,
        )


def test_no_silent_ACL_widening_between_C0_stages() -> None:
    """C0.7 anti-bypass — retrieval plan ACL scope is never broader than RouteContract.

    build_retrieval_plan intersects route.allowed_sources with preflight
    allowed_source_classes and subtracts disallowed_sources. There is no
    path that can widen scope.
    """
    route = _route(
        allowed=frozenset({"docs"}),
        disallowed=frozenset({"code"}),
    )
    p_status = preflight(route)
    assert p_status.eligible is True
    # preflight cannot include source classes not allowed by route.
    assert p_status.allowed_source_classes <= route.allowed_sources
    assert p_status.allowed_source_classes.isdisjoint(route.disallowed_sources)
    plan = build_retrieval_plan(route, p_status)
    # plan cannot widen.
    assert plan.allowed_sources <= route.allowed_sources
    assert plan.source_classes <= p_status.allowed_source_classes
    assert plan.disallowed_sources == route.disallowed_sources


def test_replay_determinism_across_full_C0_stage() -> None:
    """C0.7 anti-bypass — same inputs → same contract digest (replay-stable)."""
    route = _route()
    items = [
        _evidence(eid="a", source="doc:1", authority=0.95, lane="sparse"),
        _evidence(eid="b", source="doc:2", authority=0.60, lane="sparse"),
    ]
    # Run the full C0.4 → C0.5 path twice and confirm identical digest.

    def _run() -> FinalEvidenceContract:
        deduped = dedupe(list(items))
        shaped = stratify(deduped)
        report = scan_contradictions_and_gaps(
            shaped,
            support_target=SupportTarget.SOURCE_SUMMARY,
            high_stakes=False,
        )
        breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
        # Use a stable contract_id so digest comparison isolates *behavior* not uuid.
        contract = build_final_contract(
            route=route,
            shaped=shaped,
            report=report,
            breakdown=breakdown,
        )
        # Swap the uuid contract_id for a stable one before digesting.
        stable = FinalEvidenceContract(
            contract_id="stable-c1",
            route_id=contract.route_id,
            route_replay_key=contract.route_replay_key,
            policy_hash=contract.policy_hash,
            blueprint_hash=contract.blueprint_hash,
            status=contract.status,
            support_score=contract.support_score,
            score_breakdown=contract.score_breakdown,
            evidence=contract.evidence,
            contradiction_flags=contract.contradiction_flags,
            unresolved_gaps=contract.unresolved_gaps,
            recommended_disposition=contract.recommended_disposition,
            refine_attempts=contract.refine_attempts,
            extras=contract.extras,
        )
        return stable

    d1 = contract_digest(_run())
    d2 = contract_digest(_run())
    assert d1 == d2, f"replay produced divergent digests: {d1!r} vs {d2!r}"


# ===========================================================================
# Spec-count assertion — C0.7 mandates EXACTLY 30 named tests.
# ===========================================================================


def test_c0_7_spec_mandated_test_count_is_thirty() -> None:
    """Meta-assertion — this module defines exactly the 30 C0.7-named tests.

    11 gate-negative + 14 failure-mode-preventive + 5 stage-spanning.
    This test catches future accidental deletions of named tests.
    """
    import sys

    mod = sys.modules[__name__]
    gate_tests = [n for n in dir(mod) if n.startswith("test_c0_g")]
    failure_tests = [n for n in dir(mod) if n.startswith("test_no_")]
    stage_span_tests = [
        n
        for n in dir(mod)
        if n
        in {
            "test_no_runtime_disposition_vocabulary_in_any_C0_output",
            "test_no_durable_L4_write_attempted_from_C0",
            "test_no_route_change_emitted_from_C0",
            "test_no_silent_ACL_widening_between_C0_stages",
            "test_replay_determinism_across_full_C0_stage",
        }
    ]
    # stage_span_tests are a subset of failure_tests by prefix rule — count them
    # explicitly (the prefix 'test_no_' also matches stage-span names).
    assert len(gate_tests) == 11, f"expected 11 G0..G10 tests, got {len(gate_tests)}: {gate_tests}"
    assert len(stage_span_tests) == 5, f"expected 5 stage-spanning, got {stage_span_tests}"
    # failure-mode tests = 14; of 5 stage-span, 4 start with 'test_no_' and 1
    # ('test_replay_determinism_across_full_C0_stage') does not.
    # Therefore total test_no_* = 14 + 4 = 18.
    assert len(failure_tests) == 18, (
        f"expected 18 test_no_* tests (14 failure-mode + 4 stage-span with test_no_ prefix), "
        f"got {len(failure_tests)}: {failure_tests}"
    )
    # Total named tests in this module should be exactly 30 per C0.7 spec + 1 meta.
    all_tests = [n for n in dir(mod) if n.startswith("test_")]
    assert len(all_tests) == 31, (
        f"expected 30 C0.7-mandated tests + 1 meta-count test = 31 total, got {len(all_tests)}"
    )
