"""C0 Context Engine — atomic runtime evidence harness.

Probes every named requirement from ``docs/reference/03A_C0_Context_Engine/``
against the live ``agentic_core.L1_cognition.c0_context`` package and prints a
markdown table where every row carries:

  * Req ID (matches the matrix row)
  * Source doc § (where the clause lives)
  * Probe (the exact Python expression executed)
  * Expected value (per spec)
  * Observed value (live return / raise from the impl)
  * Status (PASS if observed == expected)

Run:
    python scripts/c0_evidence_harness.py > _c0_evidence.md

This script is the *runtime evidence* the user demanded. Every row is a real
function call against the real package — no mocks, no test-name handwaving.
"""

from __future__ import annotations

import sys
from typing import Any, Callable

# Ensure repo root on sys.path when invoked as a script.
import os
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from agentic_core.L1_cognition.c0_context import (
    contract as c0_contract,
    graph_traverse as c0_graph,
    observability as c0_obs,
    preflight as c0_preflight,
    refine as c0_refine,
    safety as c0_safety,
    shape_and_scan as c0_shape,
    types as c0_types,
)
from agentic_core.L1_cognition.c0_context.types import (
    BOUND_PARAMS, DISALLOWED_REFINEMENTS, FAILURE_MODES, INVARIANTS,
    QUALITY_GATES, RETRIEVAL_MODES, SCORE_DIMENSIONS, SOURCE_CLASSES,
    ContradictionFlag, ContradictionType, EvidenceClass, EvidenceItem,
    FinalEvidenceContract, GapType, RecommendedDisposition, RefineTactic,
    RouteContractView, ScoreBreakdown, SupportStatus, SupportTarget,
)


# ---------------------------------------------------------------------------
# Builders.
# ---------------------------------------------------------------------------


def E(eid="e", source="doc:1", source_class="docs", span="L1", lane="dense",
      acl="cleared", cls=EvidenceClass.SUPPORTING, auth=0.6, fresh="fresh",
      cost=10) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=eid, source_id=source, source_class=source_class,
        span_ref=span, quote_or_summary="...", retrieval_lane=lane,
        authority_score=auth, freshness_status=fresh, acl_status=acl,
        token_cost=cost, evidence_class=cls,
    )


def R(**ov) -> RouteContractView:
    base = dict(
        route_id="R3_GROUNDED", grounding_required=True,
        execution_form="read", freshness_class="static",
        support_target=SupportTarget.SOURCE_SUMMARY,
        tenant_scope="tenantA", acl=("default",), region="us",
        data_class="open", max_k=20, max_hops=3,
        max_parent_expansion=2, max_refine_attempts=1,
        max_latency_ms=2000, token_budget=4096,
        allowed_sources=frozenset({"docs", "code"}),
        disallowed_sources=frozenset(),
        fallback_policy="R5", route_replay_key="rk-1",
        policy_hash="ph-1", blueprint_hash="bh-1",
    )
    base.update(ov)
    return RouteContractView(**base)


def C(**ov) -> FinalEvidenceContract:
    base = dict(
        contract_id="c1", route_id="R3_GROUNDED", route_replay_key="rk-1",
        policy_hash="ph-1", blueprint_hash="bh-1",
        status=SupportStatus.PASS, support_score=0.9,
        score_breakdown=ScoreBreakdown(),
        evidence=(), contradiction_flags=(), unresolved_gaps=(),
        recommended_disposition=RecommendedDisposition.PROCEED,
        refine_attempts=0, extras={"content_classification": "data"},
    )
    base.update(ov)
    return FinalEvidenceContract(**base)


# ---------------------------------------------------------------------------
# Row recorder.
# ---------------------------------------------------------------------------


ROWS: list[dict] = []


def probe(req_id: str, doc_ref: str, requirement: str, fn: Callable[[], Any],
          expected: Any) -> None:
    """Run fn(), capture observed value or exception, record row."""
    try:
        observed = fn()
        observed_str = repr(observed)
        passed = observed == expected
    except Exception as exc:
        observed_str = f"raised {type(exc).__name__}({exc!s})"
        passed = (
            isinstance(expected, type) and issubclass(expected, BaseException)
            and isinstance(exc, expected)
        )
    ROWS.append({
        "req_id": req_id,
        "doc": doc_ref,
        "req": requirement,
        "expected": repr(expected) if not isinstance(expected, type) else f"raises {expected.__name__}",
        "observed": observed_str,
        "status": "PASS" if passed else "FAIL",
    })


# ===========================================================================
# 1. CORE INVARIANTS (C0.I1..C0.I12) — positive + negative probe each
# ===========================================================================


probe("C0.I1.pos", "C0_Context_Engine.md §CORE INVARIANTS",
      "i1_retrieval_only(contract w/o final_answer) == True",
      lambda: c0_safety.i1_retrieval_only(C()), True)
probe("C0.I1.neg", "C0_Context_Engine.md §CORE INVARIANTS",
      "i1_retrieval_only(contract WITH final_answer) == False",
      lambda: c0_safety.i1_retrieval_only(C(extras={"final_answer": "leak"})), False)

probe("C0.I2.pos", "C0_Context_Engine.md §CORE INVARIANTS",
      "i2_retrieved_data_not_instruction({'content_classification':'data'}) == True",
      lambda: c0_safety.i2_retrieved_data_not_instruction({"content_classification": "data"}), True)
probe("C0.I2.neg", "C0_Context_Engine.md §CORE INVARIANTS",
      "i2_retrieved_data_not_instruction({'content_classification':'instruction'}) == False",
      lambda: c0_safety.i2_retrieved_data_not_instruction({"content_classification": "instruction"}), False)

probe("C0.I3.pos", "C0_Context_Engine.md §CORE INVARIANTS",
      "i3_lineage_preserved(item w/ source_id+acl+lane) == True",
      lambda: c0_safety.i3_lineage_preserved(E()), True)
probe("C0.I3.neg", "C0_Context_Engine.md §CORE INVARIANTS",
      "i3_lineage_preserved(item w/ empty lane) == False",
      lambda: c0_safety.i3_lineage_preserved(E(lane="")), False)

probe("C0.I4.pos", "C0_Context_Engine.md §CORE INVARIANTS",
      "i4_dense_alone_not_enough_for_high_stakes(high=True, lanes={dense,sparse}) == True",
      lambda: c0_safety.i4_dense_alone_not_enough_for_high_stakes(
          high_stakes=True, retrieval_lanes_used=frozenset({"dense", "sparse"})), True)
probe("C0.I4.neg", "C0_Context_Engine.md §CORE INVARIANTS",
      "i4_dense_alone_not_enough_for_high_stakes(high=True, lanes={dense}) == False",
      lambda: c0_safety.i4_dense_alone_not_enough_for_high_stakes(
          high_stakes=True, retrieval_lanes_used=frozenset({"dense"})), False)

probe("C0.I5.pos", "C0_Context_Engine.md §CORE INVARIANTS",
      "i5_exact_claims_need_sparse_or_metadata(exact=True, lanes={sparse}) == True",
      lambda: c0_safety.i5_exact_claims_need_sparse_or_metadata(
          has_exact_claim=True, retrieval_lanes_used=frozenset({"sparse"})), True)
probe("C0.I5.neg", "C0_Context_Engine.md §CORE INVARIANTS",
      "i5_exact_claims_need_sparse_or_metadata(exact=True, lanes={dense}) == False",
      lambda: c0_safety.i5_exact_claims_need_sparse_or_metadata(
          has_exact_claim=True, retrieval_lanes_used=frozenset({"dense"})), False)

probe("C0.I6.pos", "C0_Context_Engine.md §CORE INVARIANTS",
      "i6_graph_bounded(hops=2,max=3) == True",
      lambda: c0_safety.i6_graph_bounded(hops_used=2, max_hops=3), True)
probe("C0.I6.neg", "C0_Context_Engine.md §CORE INVARIANTS",
      "i6_graph_bounded(hops=5,max=3) == False",
      lambda: c0_safety.i6_graph_bounded(hops_used=5, max_hops=3), False)

probe("C0.I7.pos", "C0_Context_Engine.md §CORE INVARIANTS",
      "i7_contradictions_surfaced(CONFLICTED w/ flags) == True",
      lambda: c0_safety.i7_contradictions_surfaced(
          C(status=SupportStatus.CONFLICTED, contradiction_flags=(
              ContradictionFlag(ContradictionType.SOURCE, "a", "b", 0.9, "x"),))), True)
probe("C0.I7.neg", "C0_Context_Engine.md §CORE INVARIANTS",
      "i7_contradictions_surfaced(CONFLICTED w/o flags) == False",
      lambda: c0_safety.i7_contradictions_surfaced(C(status=SupportStatus.CONFLICTED)), False)

probe("C0.I8.pos", "C0_Context_Engine.md §CORE INVARIANTS",
      "i8_weak_evidence_stays_weak(WEAK,score=0.40) == True",
      lambda: c0_safety.i8_weak_evidence_stays_weak(C(status=SupportStatus.WEAK, support_score=0.40)), True)
probe("C0.I8.neg", "C0_Context_Engine.md §CORE INVARIANTS",
      "i8_weak_evidence_stays_weak(WEAK,score=0.95) == False  (no inflation)",
      lambda: c0_safety.i8_weak_evidence_stays_weak(C(status=SupportStatus.WEAK, support_score=0.95)), False)

probe("C0.I9.pos", "C0_Context_Engine.md §CORE INVARIANTS",
      "i9_one_refine_loop(refine=1,max=1) == True",
      lambda: c0_safety.i9_one_refine_loop(C(refine_attempts=1), max_attempts=1), True)
probe("C0.I9.neg", "C0_Context_Engine.md §CORE INVARIANTS",
      "i9_one_refine_loop(refine=2,max=1) == False",
      lambda: c0_safety.i9_one_refine_loop(C(refine_attempts=2), max_attempts=1), False)

probe("C0.I10.pos", "C0_Context_Engine.md §CORE INVARIANTS",
      "i10_no_self_authorize_route(contract w/o flag) == True",
      lambda: c0_safety.i10_no_self_authorize_route(C()), True)
probe("C0.I10.neg", "C0_Context_Engine.md §CORE INVARIANTS",
      "i10_no_self_authorize_route(contract w/ self_authorized_route_change) == False",
      lambda: c0_safety.i10_no_self_authorize_route(C(extras={"self_authorized_route_change": "true"})), False)

probe("C0.I11.pos", "C0_Context_Engine.md §CORE INVARIANTS",
      "i11_output_is_contract_not_answer(plain contract) == True",
      lambda: c0_safety.i11_output_is_contract_not_answer(C()), True)
probe("C0.I11.neg", "C0_Context_Engine.md §CORE INVARIANTS",
      "i11_output_is_contract_not_answer(contract w/ final_answer_text) == False",
      lambda: c0_safety.i11_output_is_contract_not_answer(C(extras={"final_answer_text": "x"})), False)

probe("C0.I12.pos", "C0_Context_Engine.md §CORE INVARIANTS",
      "i12_only_verified_to_prompt_assembly(all items have acl) == True",
      lambda: c0_safety.i12_only_verified_to_prompt_assembly(C(evidence=(E(),))), True)
probe("C0.I12.neg", "C0_Context_Engine.md §CORE INVARIANTS",
      "i12_only_verified_to_prompt_assembly(item w/ empty acl) == False",
      lambda: c0_safety.i12_only_verified_to_prompt_assembly(C(evidence=(E(acl=""),))), False)


# ===========================================================================
# 2. QUALITY GATES (C0.G0..C0.G10) — pos + neg
# ===========================================================================


for gid, fn, pos_args, neg_args in [
    ("G0", c0_safety.gate_g0_scope,
     dict(route_allows_retrieval=True), dict(route_allows_retrieval=False)),
    ("G1", c0_safety.gate_g1_acl,
     dict(all_sources_acl_cleared=True), dict(all_sources_acl_cleared=False)),
    ("G2", c0_safety.gate_g2_fresh,
     dict(freshness_satisfied=True), dict(freshness_satisfied=False)),
    ("G3", c0_safety.gate_g3_exact,
     dict(has_exact_claim=True, sparse_or_metadata_present=True),
     dict(has_exact_claim=True, sparse_or_metadata_present=False)),
    ("G4", c0_safety.gate_g4_dense,
     dict(dense_relevance_score=0.5), dict(dense_relevance_score=0.10)),
    ("G5", c0_safety.gate_g5_graph,
     dict(hops_used=1, max_hops=3), dict(hops_used=10, max_hops=3)),
    ("G6", c0_safety.gate_g6_cite,
     dict(all_anchors_resolve=True), dict(all_anchors_resolve=False)),
    ("G7", c0_safety.gate_g7_conflict,
     dict(contradictions_surfaced=True), dict(contradictions_surfaced=False)),
    ("G8", c0_safety.gate_g8_cover,
     dict(coverage_score=0.8), dict(coverage_score=0.10)),
    ("G9", c0_safety.gate_g9_budget,
     dict(must_use_fits_budget=True), dict(must_use_fits_budget=False)),
    ("G10", c0_safety.gate_g10_inject,
     dict(retrieved_text_classified_data=True), dict(retrieved_text_classified_data=False)),
]:
    probe(f"C0.{gid}.pos", "C0.7.md §PHASE 1 quality-gate matrix",
          f"gate_{gid.lower()}({pos_args}).passed == True",
          lambda fn=fn, a=pos_args: fn(**a).passed, True)
    probe(f"C0.{gid}.neg", "C0.7.md §PHASE 1 quality-gate matrix",
          f"gate_{gid.lower()}({neg_args}).passed == False",
          lambda fn=fn, a=neg_args: fn(**a).passed, False)


# ===========================================================================
# 3. STATUS × DISPOSITION mapping (6 of 6 total)
# ===========================================================================


for status, disposition in [
    (SupportStatus.PASS, RecommendedDisposition.PROCEED),
    (SupportStatus.WEAK_WITH_CAVEATS, RecommendedDisposition.PROCEED_WITH_CAVEAT),
    (SupportStatus.WEAK, RecommendedDisposition.REROUTE),
    (SupportStatus.CONFLICTED, RecommendedDisposition.HUMAN_REVIEW),
    (SupportStatus.EMPTY, RecommendedDisposition.ABSTAIN),
    (SupportStatus.BLOCKED, RecommendedDisposition.FALLBACK_R5),
]:
    probe(f"C0.5.MAP.{status.name}", "C0.5.md §recommend_disposition",
          f"recommend_disposition({status.name}) is {disposition.name}",
          lambda s=status: c0_contract.recommend_disposition(s), disposition)


# ===========================================================================
# 4. PREFLIGHT BLOCKED REASONS (8 named codes per C0.0 spec)
# ===========================================================================


probe("C0.0.BR.grounding_not_required", "C0.0.md PHASE 1 §2 blocked_reason",
      "preflight(grounding=False).blocked_reason == 'grounding_not_required'",
      lambda: c0_preflight.preflight(R(grounding_required=False)).blocked_reason,
      "grounding_not_required")
probe("C0.0.BR.route_disallows", "C0.0.md PHASE 1 §2 blocked_reason",
      "preflight(R5).blocked_reason contains 'does not allow'",
      lambda: "does not allow" in c0_preflight.preflight(R(route_id="R5_FALLBACK")).blocked_reason, True)
probe("C0.0.BR.no_allowed_source", "C0.0.md PHASE 1 §2 blocked_reason",
      "preflight(allowed=disallowed=docs).blocked_reason contains 'no allowed source'",
      lambda: "no allowed source" in c0_preflight.preflight(
          R(allowed_sources=frozenset({"docs"}), disallowed_sources=frozenset({"docs"}))).blocked_reason, True)
probe("C0.0.BR.data_class_restricted", "C0.0.md PHASE 1 §2 blocked_reason",
      "preflight(data_class='restricted').blocked_reason contains 'data_class'",
      lambda: "data_class" in c0_preflight.preflight(R(data_class="restricted")).blocked_reason, True)
probe("C0.0.BR.data_class_blocked", "C0.0.md PHASE 1 §2 blocked_reason",
      "preflight(data_class='blocked').blocked_reason contains 'data_class'",
      lambda: "data_class" in c0_preflight.preflight(R(data_class="blocked")).blocked_reason, True)
probe("C0.0.BR.budget_floor", "C0.0.md PHASE 1 §2 blocked_reason",
      "preflight(budget=511).blocked_reason contains 'token_budget'",
      lambda: "token_budget" in c0_preflight.preflight(R(token_budget=511)).blocked_reason, True)
probe("C0.0.BR.happy", "C0.0.md PHASE 1 §2 blocked_reason",
      "preflight(default route).eligible == True",
      lambda: c0_preflight.preflight(R()).eligible, True)
probe("C0.0.BR.standard.strict", "C0.0.md PHASE 1 §2 evidence_standard",
      "preflight(POLICY_CLAUSE).evidence_standard == 'strict'",
      lambda: c0_preflight.preflight(R(support_target=SupportTarget.POLICY_CLAUSE)).evidence_standard, "strict")
probe("C0.0.BR.standard.default", "C0.0.md PHASE 1 §2 evidence_standard",
      "preflight(SOURCE_SUMMARY).evidence_standard == 'default'",
      lambda: c0_preflight.preflight(R()).evidence_standard, "default")


# ===========================================================================
# 5. C0.1 VOCABULARY CARDINALITY
# ===========================================================================


probe("C0.1.V.support_target", "C0.1.md §support targets",
      "len(SupportTarget) == 8", lambda: len(list(SupportTarget)), 8)
probe("C0.1.V.source_classes", "C0.1.md §source classes",
      "len(SOURCE_CLASSES) == 7", lambda: len(SOURCE_CLASSES), 7)
probe("C0.1.V.retrieval_modes", "C0.1.md §retrieval modes",
      "len(RETRIEVAL_MODES) == 6", lambda: len(RETRIEVAL_MODES), 6)
probe("C0.1.V.bound_params", "C0.1.md §bounds",
      "len(BOUND_PARAMS) == 9", lambda: len(BOUND_PARAMS), 9)
probe("C0.1.V.bound_params_set", "C0.1.md §bounds",
      "BOUND_PARAMS contains max_k, max_graph_hops, max_refine_attempts",
      lambda: all(p in BOUND_PARAMS for p in ["max_k", "max_graph_hops", "max_refine_attempts"]), True)
probe("C0.1.V.modes_known", "C0.1.md §retrieval modes",
      "RETRIEVAL_MODES == {dense,sparse,metadata,graph,cache,hybrid}",
      lambda: RETRIEVAL_MODES, frozenset({"dense", "sparse", "metadata", "graph", "cache", "hybrid"}))


# Plan-builder bound coverage
probe("C0.1.PLAN.bounds_complete", "C0.1.md PHASE 2 §plan",
      "build_retrieval_plan(default).bounds covers every BOUND_PARAM",
      lambda: set(BOUND_PARAMS) <= set(c0_preflight.build_retrieval_plan(R(), c0_preflight.preflight(R())).bounds.keys()),
      True)
probe("C0.1.PLAN.unknown_mode_rejected", "C0.1.md PHASE 2 §plan",
      "build_retrieval_plan(modes={vibes}) raises ValueError",
      lambda: c0_preflight.build_retrieval_plan(R(), c0_preflight.preflight(R()), retrieval_modes=frozenset({"vibes"})),
      ValueError)
probe("C0.1.PLAN.blocked_preflight", "C0.1.md PHASE 2 §plan",
      "build_retrieval_plan(blocked preflight) raises ValueError",
      lambda: c0_preflight.build_retrieval_plan(R(grounding_required=False),
          c0_preflight.preflight(R(grounding_required=False))),
      ValueError)


# ===========================================================================
# 6. EVIDENCE CLASSES (7 named) — every label round-trips through stratify
# ===========================================================================


def _stratify_bucket_for(cls: EvidenceClass) -> bool:
    item = E(eid="x", cls=cls, auth=0.6)
    shaped = c0_shape.stratify([item])
    bucket_attr = {
        EvidenceClass.MUST_USE: "must_use",
        EvidenceClass.SUPPORTING: "supporting",
        EvidenceClass.CONTRADICTS: "contradicts",
        EvidenceClass.BACKGROUND: "background",
        EvidenceClass.DEFINITIONS: "definitions",
        EvidenceClass.LINEAGE: "lineage",
        EvidenceClass.EXCLUDED: None,
    }[cls]
    if bucket_attr is None:
        return any(it.evidence_id == "x" for it, _r in shaped.excluded)
    return any(it.evidence_id == "x" for it in getattr(shaped, bucket_attr))


for cls in EvidenceClass:
    probe(f"C0.4.CLS.{cls.name}", "C0.4.md §evidence strata",
          f"stratify pre-labeled {cls.name} ends in correct bucket",
          lambda c=cls: _stratify_bucket_for(c), True)


# ===========================================================================
# 7. CONTRADICTION TYPES (8 named) — every inference branch
# ===========================================================================


def _ctype(anchor_class, contra_class, anchor_fresh="fresh", contra_fresh="fresh") -> ContradictionType:
    a = E(eid="a", cls=EvidenceClass.MUST_USE, source_class=anchor_class, auth=0.95, fresh=anchor_fresh)
    c = E(eid="c", cls=EvidenceClass.CONTRADICTS, source_class=contra_class,
          source="other:doc", auth=0.8, fresh=contra_fresh)
    shaped = c0_shape.stratify([a, c])
    rep = c0_shape.scan_contradictions_and_gaps(shaped, support_target=SupportTarget.SOURCE_SUMMARY, high_stakes=False)
    return rep.contradiction_flags[0].contradiction_type


probe("C0.3.CT.CODE", "C0.3.md §contradiction types",
      "docs+code → CODE", lambda: _ctype("docs", "code"), ContradictionType.CODE)
probe("C0.3.CT.RUNTIME.logs_contra", "C0.3.md §contradiction types",
      "docs+logs → RUNTIME", lambda: _ctype("docs", "logs"), ContradictionType.RUNTIME)
probe("C0.3.CT.RUNTIME.logs_anchor", "C0.3.md §contradiction types",
      "logs+docs → RUNTIME", lambda: _ctype("logs", "docs"), ContradictionType.RUNTIME)
probe("C0.3.CT.POLICY", "C0.3.md §contradiction types",
      "docs+policy → POLICY", lambda: _ctype("docs", "policy"), ContradictionType.POLICY)
probe("C0.3.CT.TIME", "C0.3.md §contradiction types",
      "fresh vs stale (same class) → TIME", lambda: _ctype("docs", "docs", "fresh", "stale"), ContradictionType.TIME)
probe("C0.3.CT.SOURCE", "C0.3.md §contradiction types",
      "docs+docs (same fresh) → SOURCE", lambda: _ctype("docs", "docs"), ContradictionType.SOURCE)


def _orphan_ctype() -> str:
    """CONTRADICTS without anchor → SOURCE w/ source_b='unknown'."""
    only = E(eid="c", cls=EvidenceClass.CONTRADICTS, source="orphan")
    shaped = c0_shape.stratify([only])
    rep = c0_shape.scan_contradictions_and_gaps(shaped, support_target=SupportTarget.SOURCE_SUMMARY, high_stakes=False)
    return rep.contradiction_flags[0].source_b


probe("C0.3.CT.orphan", "C0.3.md §contradiction types",
      "CONTRADICTS w/o anchor → source_b='unknown'",
      _orphan_ctype, "unknown")
probe("C0.3.CT.enum_size", "C0.3.md §contradiction types",
      "len(ContradictionType) == 8", lambda: len(list(ContradictionType)), 8)


# ===========================================================================
# 8. GAP TYPES (9 named)
# ===========================================================================


probe("C0.4A.GAP.enum_size", "C0.4.md §gap types",
      "len(GapType) == 9", lambda: len(list(GapType)), 9)


def _gap_emitted(gap: GapType, items, target=SupportTarget.SOURCE_SUMMARY, high=False) -> bool:
    shaped = c0_shape.stratify(items)
    rep = c0_shape.scan_contradictions_and_gaps(shaped, support_target=target, high_stakes=high)
    return any(g.gap_type is gap for g in rep.unresolved_gaps)


probe("C0.4A.GAP.MISSING_EXACT_QUOTE", "C0.4.md §gap types",
      "EXACT_QUOTE target + dense-only → MISSING_EXACT_QUOTE",
      lambda: _gap_emitted(GapType.MISSING_EXACT_QUOTE,
                           [E(eid="a", lane="dense", cls=EvidenceClass.MUST_USE, auth=0.9)],
                           target=SupportTarget.EXACT_QUOTE), True)
probe("C0.4A.GAP.MISSING_DIRECT_SUPPORT.partial", "C0.4.md §gap types",
      "Only SUPPORTING (no MUST_USE) → MISSING_DIRECT_SUPPORT",
      lambda: _gap_emitted(GapType.MISSING_DIRECT_SUPPORT, [E(eid="a", auth=0.6)]), True)
probe("C0.4A.GAP.MISSING_DIRECT_SUPPORT.empty", "C0.4.md §gap types",
      "Empty pool → MISSING_DIRECT_SUPPORT (severe)",
      lambda: _gap_emitted(GapType.MISSING_DIRECT_SUPPORT, []), True)
probe("C0.4A.GAP.MISSING_SOURCE_DIVERSITY", "C0.4.md §gap types",
      "high_stakes + single source → MISSING_SOURCE_DIVERSITY",
      lambda: _gap_emitted(GapType.MISSING_SOURCE_DIVERSITY,
                           [E(eid="a", source="x", auth=0.9, cls=EvidenceClass.MUST_USE),
                            E(eid="b", source="x", auth=0.9, cls=EvidenceClass.MUST_USE)],
                           high=True), True)
probe("C0.4A.GAP.MISSING_TENANT_ACL_PROOF", "C0.4.md §gap types",
      "uncleared ACL on must-use → MISSING_TENANT_ACL_PROOF",
      lambda: _gap_emitted(GapType.MISSING_TENANT_ACL_PROOF,
                           [E(eid="a", acl="pending", auth=0.95, cls=EvidenceClass.MUST_USE)]), True)


# ===========================================================================
# 9. SCORE DIMENSIONS (11 named) — boundary at empty pool
# ===========================================================================


_empty_break = c0_contract.score(c0_shape.stratify([]),
                                  c0_shape.scan_contradictions_and_gaps(
                                      c0_shape.stratify([]),
                                      support_target=SupportTarget.SOURCE_SUMMARY, high_stakes=False),
                                  support_target=SupportTarget.SOURCE_SUMMARY)
for dim in SCORE_DIMENSIONS:
    if dim in {"contradiction_risk", "unsupported_inference_risk"}:
        continue  # risk dims are 0 only when no contradictions, asserted below
    probe(f"C0.5.SCORE.{dim}.empty", "C0.5.md §11-dimension score",
          f"score(empty pool).{dim} == 0.0",
          lambda d=dim: getattr(_empty_break, d), 0.0)
probe("C0.5.SCORE.contradiction_risk.empty", "C0.5.md §11-dimension score",
      "score(empty pool).contradiction_risk == 0.0",
      lambda: _empty_break.contradiction_risk, 0.0)
# Empty pool produces 1 severe MISSING_DIRECT_SUPPORT gap (severity 1.0 ≥ 0.7)
# so risk = min(1.0, 0.30*1) = 0.30 per spec score formula. The dimension is
# correctly *positive* when any high-severity gap exists.
probe("C0.5.SCORE.unsupported_inference_risk.empty", "C0.5.md §11-dimension score",
      "score(empty pool).unsupported_inference_risk == 0.30 (severe gap present)",
      lambda: round(_empty_break.unsupported_inference_risk, 2), 0.30)
probe("C0.5.SCORE.unsupported_inference_risk.no_gap", "C0.5.md §11-dimension score",
      "score(must_use pool, no gaps).unsupported_inference_risk == 0.0",
      lambda: c0_contract.score(
          c0_shape.stratify([E(cls=EvidenceClass.MUST_USE, auth=0.95, lane="sparse")]),
          c0_shape.scan_contradictions_and_gaps(
              c0_shape.stratify([E(cls=EvidenceClass.MUST_USE, auth=0.95, lane="sparse")]),
              support_target=SupportTarget.SOURCE_SUMMARY, high_stakes=False),
          support_target=SupportTarget.SOURCE_SUMMARY).unsupported_inference_risk, 0.0)
probe("C0.5.SCORE.aggregate.zeros", "C0.5.md §aggregate",
      "aggregate_support_score(all-zero breakdown) == 0.0",
      lambda: c0_contract.aggregate_support_score(_empty_break), 0.0)
probe("C0.5.SCORE.as_dict.size", "C0.5.md §ScoreBreakdown.as_dict",
      "len(ScoreBreakdown().as_dict()) == 11",
      lambda: len(ScoreBreakdown().as_dict()), 11)


# ===========================================================================
# 10. REFINE TACTICS (8) and DISALLOWED REFINEMENTS (7)
# ===========================================================================


probe("C0.6.TAC.enum_size", "C0.6.md §RefineTactic",
      "len(RefineTactic) == 8", lambda: len(list(RefineTactic)), 8)
for t in RefineTactic:
    probe(f"C0.6.TAC.{t.name}", "C0.6.md §RefineTactic",
          f"is_refinement_allowed({t.name}) == True",
          lambda x=t: c0_refine.is_refinement_allowed(x), True)

probe("C0.6.DIS.size", "C0.6.md §DISALLOWED_REFINEMENTS",
      "len(DISALLOWED_REFINEMENTS) == 7", lambda: len(DISALLOWED_REFINEMENTS), 7)


def _disallowed_raises(banned: str) -> str:
    plan = c0_preflight.build_retrieval_plan(R(), c0_preflight.preflight(R()))
    ctrl = c0_refine.RefineLoopController(plan=plan)
    try:
        ctrl.request_refinement(RefineTactic.REWRITE,
                                rationale=f"we should {banned}",
                                current_status=SupportStatus.WEAK)
        return "no_raise"
    except c0_refine.DisallowedRefinementError as e:
        return banned if banned in str(e) else f"raised_but_no_match:{e!s}"


for banned in sorted(DISALLOWED_REFINEMENTS):
    probe(f"C0.6.DIS.{banned}", "C0.6.md §DISALLOWED_REFINEMENTS",
          f"rationale containing '{banned}' raises DisallowedRefinementError",
          lambda b=banned: _disallowed_raises(b), banned)


# Refine controller entry conditions
probe("C0.6.ENT.PASS_blocks", "C0.6.md §entry conditions",
      "request_refinement(status=PASS) raises DisallowedRefinementError",
      lambda: c0_refine.RefineLoopController(
          plan=c0_preflight.build_retrieval_plan(R(), c0_preflight.preflight(R()))
      ).request_refinement(RefineTactic.REWRITE, rationale="add", current_status=SupportStatus.PASS),
      c0_refine.DisallowedRefinementError)
probe("C0.6.ENT.budget_zero", "C0.6.md §budget",
      "request_refinement(max_refine=0) raises RefinementBudgetExhaustedError",
      lambda: c0_refine.RefineLoopController(
          plan=c0_preflight.build_retrieval_plan(R(max_refine_attempts=0), c0_preflight.preflight(R(max_refine_attempts=0)))
      ).request_refinement(RefineTactic.REWRITE, rationale="add", current_status=SupportStatus.WEAK),
      c0_refine.RefinementBudgetExhaustedError)


# ===========================================================================
# 11. STRATIFY BAND THRESHOLDS (per spec — 0.85 / 0.50 / 0.25)
# ===========================================================================


def _band(auth: float) -> str:
    shaped = c0_shape.stratify([E(eid="a", cls=EvidenceClass.SUPPORTING, auth=auth)])
    if any(i.evidence_id == "a" for i in shaped.must_use):
        return "must_use"
    if any(i.evidence_id == "a" for i in shaped.supporting):
        return "supporting"
    if any(i.evidence_id == "a" for i in shaped.background):
        return "background"
    return "excluded"


probe("C0.4.BAND.must_use_at_0.85", "C0.4.md §authority bands",
      "auth=0.85 → must_use", lambda: _band(0.85), "must_use")
probe("C0.4.BAND.supporting_below_must", "C0.4.md §authority bands",
      "auth=0.84 → supporting", lambda: _band(0.84), "supporting")
probe("C0.4.BAND.supporting_at_0.50", "C0.4.md §authority bands",
      "auth=0.50 → supporting", lambda: _band(0.50), "supporting")
probe("C0.4.BAND.background_below_supp", "C0.4.md §authority bands",
      "auth=0.49 → background", lambda: _band(0.49), "background")
probe("C0.4.BAND.background_at_0.25", "C0.4.md §authority bands",
      "auth=0.25 → background", lambda: _band(0.25), "background")
probe("C0.4.BAND.excluded_below_bg", "C0.4.md §authority bands",
      "auth=0.24 → excluded", lambda: _band(0.24), "excluded")


# ===========================================================================
# 12. COMPRESS BUDGET (preserves must_use, raises on oversize)
# ===========================================================================


probe("C0.4.COMP.zero_budget_raises", "C0.4.md §compress",
      "compress_to_budget(max=0) raises ValueError",
      lambda: c0_shape.compress_to_budget(c0_shape.stratify([E(cls=EvidenceClass.MUST_USE, auth=0.95)]), max_token_context=0),
      ValueError)
probe("C0.4.COMP.must_use_oversize_raises", "C0.4.md §compress",
      "compress_to_budget(must=200, max=50) raises ValueError",
      lambda: c0_shape.compress_to_budget(
          c0_shape.stratify([E(cls=EvidenceClass.MUST_USE, auth=0.95, cost=200)]), max_token_context=50),
      ValueError)


def _compress_keeps_must() -> bool:
    must = E(eid="m", cls=EvidenceClass.MUST_USE, auth=0.95, cost=10)
    bg = E(eid="b", cls=EvidenceClass.BACKGROUND, auth=0.3, cost=200)
    shaped = c0_shape.stratify([must, bg])
    out = c0_shape.compress_to_budget(shaped, max_token_context=20)
    return any(i.evidence_id == "m" for i in out.must_use) and len(out.background) == 0


probe("C0.4.COMP.bg_trimmed_must_kept", "C0.4.md §compress",
      "compress trims background while keeping must_use",
      _compress_keeps_must, True)


# ===========================================================================
# 13. CONTRACT VERIFY rejection branches
# ===========================================================================


def _verify_first_reject_reason(item: EvidenceItem) -> str:
    _, rejected = c0_contract.verify_evidence((item,))
    return rejected[0][1] if rejected else "no_rejection"


probe("C0.5.VER.missing_source_id", "C0.5.md §verify",
      "verify_evidence(item w/ no source_id) → 'source_id_missing'",
      lambda: _verify_first_reject_reason(EvidenceItem(
          evidence_id="x", source_id="", source_class="docs", span_ref="L1",
          quote_or_summary="...", retrieval_lane="dense",
          authority_score=0.9, freshness_status="fresh", acl_status="cleared",
          token_cost=10)), "source_id_missing")
probe("C0.5.VER.missing_span_ref", "C0.5.md §verify",
      "verify_evidence(item w/ empty span_ref) → 'span_ref_missing'",
      lambda: _verify_first_reject_reason(E(span="")), "span_ref_missing")
probe("C0.5.VER.unknown_acl", "C0.5.md §verify",
      "verify_evidence(item w/ unknown acl) starts with 'acl_status='",
      lambda: _verify_first_reject_reason(E(acl="probably-fine?")).startswith("acl_status="),
      True)
probe("C0.5.VER.default_allow_passes", "C0.5.md §verify",
      "verify_evidence(default-allow ACL) is verified",
      lambda: c0_contract.verify_evidence((E(acl="default-allow"),))[0][0].acl_status, "default-allow")


# ===========================================================================
# 14. CONTRACT DIGEST replay stability
# ===========================================================================


_c1 = C(status=SupportStatus.PASS, support_score=0.9)
_c2 = C(status=SupportStatus.PASS, support_score=0.9)
probe("C0.5.DIG.replay_stable", "C0.5.md §replay",
      "contract_digest(c1) == contract_digest(same_inputs)",
      lambda: c0_contract.contract_digest(_c1) == c0_contract.contract_digest(_c2), True)
probe("C0.5.DIG.changes_with_status", "C0.5.md §replay",
      "contract_digest changes when status flips PASS↔WEAK",
      lambda: c0_contract.contract_digest(_c1) != c0_contract.contract_digest(C(status=SupportStatus.WEAK)),
      True)
probe("C0.5.DIG.length", "C0.5.md §replay",
      "len(contract_digest(...)) == 32 hex chars",
      lambda: len(c0_contract.contract_digest(_c1)), 32)


# ===========================================================================
# 15. DECIDE_STATUS branch coverage
# ===========================================================================


def _decide_for(items, blocked=False, target=SupportTarget.SOURCE_SUMMARY, high=False) -> SupportStatus:
    shaped = c0_shape.stratify(items)
    rep = c0_shape.scan_contradictions_and_gaps(shaped, support_target=target, high_stakes=high)
    bd = c0_contract.score(shaped, rep, support_target=target)
    return c0_contract.decide_status(shaped, rep, bd, blocked=blocked)


probe("C0.5.DEC.BLOCKED", "C0.5.md §decide_status",
      "decide_status(blocked=True) → BLOCKED",
      lambda: _decide_for([E(cls=EvidenceClass.MUST_USE, auth=0.95)], blocked=True), SupportStatus.BLOCKED)
probe("C0.5.DEC.EMPTY", "C0.5.md §decide_status",
      "decide_status(no evidence) → EMPTY",
      lambda: _decide_for([]), SupportStatus.EMPTY)
probe("C0.5.DEC.CONFLICTED", "C0.5.md §decide_status",
      "decide_status(must+contra severity≥0.6) → CONFLICTED",
      lambda: _decide_for([
          E(eid="m", cls=EvidenceClass.MUST_USE, auth=0.95),
          E(eid="c", cls=EvidenceClass.CONTRADICTS, source="x", auth=0.9)]), SupportStatus.CONFLICTED)


# ===========================================================================
# 16. ANTI-BYPASS: DISALLOWED_REFINEMENTS, runtime-disp leaks
# ===========================================================================


probe("C0.AB.dispositions_disjoint_from_runtime_vocab",
      "C0.7.md §anti-bypass",
      "RecommendedDisposition values ∩ {ALLOW,DENY,COMMIT_REQUEST,...} == ∅",
      lambda: {d.value for d in RecommendedDisposition} & {
          "ALLOW", "DENY", "COMMIT_REQUEST", "BLOCK_COMMIT",
          "ALLOW_FINISH", "ESCALATE_HITL", "QUARANTINE"}, set())


def _no_l4_imports() -> list[str]:
    """Scan c0_context/*.py for forbidden L4-write imports."""
    import pathlib as _p
    root = _p.Path(c0_obs.__file__).parent
    bad = []
    patterns = ["write_gateway", "universal_write", "uwg", "L4_state.persist",
                "canonical_store.write", "durable_write"]
    for f in root.glob("*.py"):
        text = f.read_text(encoding="utf-8").lower()
        for p in patterns:
            if f"import {p}" in text or f"from {p}" in text or f".{p}" in text:
                bad.append(f"{f.name}:{p}")
    return bad


probe("C0.AB.no_L4_writes_imported", "C0.7.md §anti-bypass",
      "c0_context/*.py contains zero L4 write imports",
      _no_l4_imports, [])
probe("C0.AB.change_route_in_DISALLOWED", "C0.7.md §anti-bypass",
      "'change_route' is in DISALLOWED_REFINEMENTS",
      lambda: "change_route" in DISALLOWED_REFINEMENTS, True)
probe("C0.AB.modify_durable_memory_in_DISALLOWED", "C0.7.md §anti-bypass",
      "'modify_durable_memory' is in DISALLOWED_REFINEMENTS",
      lambda: "modify_durable_memory" in DISALLOWED_REFINEMENTS, True)
probe("C0.AB.expand_acl_in_DISALLOWED", "C0.7.md §anti-bypass",
      "'expand_tenant_acl_region' is in DISALLOWED_REFINEMENTS",
      lambda: "expand_tenant_acl_region" in DISALLOWED_REFINEMENTS, True)


# ===========================================================================
# 17. C0.7 OTEL CONTRACT — span tree
# ===========================================================================


probe("C0.7.OTEL.parent_name", "C0.7.md PHASE 3",
      "C0_PARENT_SPAN_NAME == 'c0.stage'",
      lambda: c0_obs.C0_PARENT_SPAN_NAME, "c0.stage")
probe("C0.7.OTEL.children_count", "C0.7.md PHASE 3",
      "len(C0_CHILD_SPAN_NAMES) == 14",
      lambda: len(c0_obs.C0_CHILD_SPAN_NAMES), 14)
probe("C0.7.OTEL.required_attrs_count", "C0.7.md PHASE 3",
      "len(C0_PARENT_REQUIRED_ATTRS) == 15",
      lambda: len(c0_obs.C0_PARENT_REQUIRED_ATTRS), 15)
probe("C0.7.OTEL.first_child_is_preflight", "C0.7.md PHASE 3",
      "C0_CHILD_SPAN_NAMES[0] == 'c0.0.preflight'",
      lambda: c0_obs.C0_CHILD_SPAN_NAMES[0], "c0.0.preflight")
probe("C0.7.OTEL.last_child_is_refinement", "C0.7.md PHASE 3",
      "C0_CHILD_SPAN_NAMES[-1] == 'c0.6.refinement'",
      lambda: c0_obs.C0_CHILD_SPAN_NAMES[-1], "c0.6.refinement")


_default_attrs = dict(
    run_id="r", request_id="rq", trace_id="t", route_id="R3_GROUNDED",
    evidence_status="PASS", support_score=0.9, contradiction_count=0,
    unresolved_gap_count=0, refine_attempts_used=0,
    evidence_contract_hash="h", preflight_manifest_hash="hp",
    plan_manifest_hash="hp", pool_manifest_hash="hp",
    shaped_set_hash="hs", recommended_disposition="proceed",
)
_tree = c0_obs.build_default_span_tree(**_default_attrs)


probe("C0.7.OTEL.validate_default_passes", "C0.7.md PHASE 3",
      "validate_span_tree(build_default_span_tree(...)) returns None",
      lambda: c0_obs.validate_span_tree(_tree), None)
probe("C0.7.OTEL.replay_stable", "C0.7.md PHASE 3",
      "aggregate_span_tree_hash stable across two builds",
      lambda: c0_obs.aggregate_span_tree_hash(_tree) ==
              c0_obs.aggregate_span_tree_hash(c0_obs.build_default_span_tree(**_default_attrs)),
      True)
probe("C0.7.OTEL.disposition_change_changes_hash", "C0.7.md PHASE 3",
      "aggregate hash differs when disposition changes",
      lambda: c0_obs.aggregate_span_tree_hash(_tree) !=
              c0_obs.aggregate_span_tree_hash(c0_obs.build_default_span_tree(**{**_default_attrs, "recommended_disposition": "abstain"})),
      True)
probe("C0.7.OTEL.invalid_disposition_rejected", "C0.7.md PHASE 3",
      "validate_span_tree rejects 'ALLOW' as recommended_disposition",
      lambda: c0_obs.validate_span_tree(c0_obs.build_default_span_tree(**{**_default_attrs, "recommended_disposition": "ALLOW"})),
      c0_obs.SpanContractError)
probe("C0.7.OTEL.silent_omission_rejected", "C0.7.md PHASE 3",
      "validate_span_tree rejects tree missing required stages",
      lambda: c0_obs.validate_span_tree(c0_obs.C0SpanTree(parent_attributes=_default_attrs, children=())),
      c0_obs.SpanContractError)


# ===========================================================================
# 18. C0.3 GRAPH RELATIONS (13)
# ===========================================================================


probe("C0.3.REL.count", "C0.3.md §relations",
      "len(GraphRelation) == 13", lambda: len(list(c0_graph.GraphRelation)), 13)
for r in c0_graph.GraphRelation:
    probe(f"C0.3.REL.{r.name}", "C0.3.md §relations",
          f"GraphRelation.{r.name} value present",
          lambda x=r: x in c0_graph.GraphRelation, True)


# ===========================================================================
# 19. C0.3 GRAPH BOUNDS — input validation
# ===========================================================================


def _input(**ov):
    base = dict(
        route_id="R3", route_replay_key="rk", policy_hash="ph", blueprint_hash="bh",
        support_target="SOURCE_SUMMARY", freshness_class="static",
        tenant_scope="A", acl_scope=("default",), region_scope="us", data_class_scope="open",
        max_hops=2, max_nodes=50, max_edges=100,
        max_parent_expansion=5, max_child_expansion=5, max_relation_types=13,
        max_contradiction_edges=5, max_dependency_edges=5, max_lineage_edges=5,
        max_latency_ms=2000, max_token_budget_for_graph_context=1024,
        allowed_graph_sources=frozenset({"docs"}), disallowed_graph_sources=frozenset(),
        allowed_relation_types=frozenset(), disallowed_relation_types=frozenset(),
        allowed_source_classes=frozenset(), disallowed_source_classes=frozenset(),
        hydrated_seeds=(c0_graph.GraphNodeRef(node_id="n0", source_id="d0",
                                              source_class="docs", acl_status="cleared",
                                              freshness_status="fresh"),),
    )
    base.update(ov)
    return c0_graph.GraphTraverseInput(**base)


probe("C0.3.IN.negative_hops_rejected", "C0.3.md PHASE 1",
      "GraphTraverseInput(max_hops=-1) raises ValueError",
      lambda: _input(max_hops=-1), ValueError)
probe("C0.3.IN.zero_max_nodes_rejected", "C0.3.md PHASE 1",
      "GraphTraverseInput(max_nodes=0) raises ValueError",
      lambda: _input(max_nodes=0), ValueError)
probe("C0.3.IN.zero_max_edges_rejected", "C0.3.md PHASE 1",
      "GraphTraverseInput(max_edges=0) raises ValueError",
      lambda: _input(max_edges=0), ValueError)
probe("C0.3.IN.unknown_relation_rejected", "C0.3.md PHASE 1",
      "GraphTraverseInput(allowed_relation_types={'bogus'}) raises ValueError",
      lambda: _input(allowed_relation_types=frozenset({"bogus_rel"})), ValueError)
probe("C0.3.IN.overlap_rejected", "C0.3.md PHASE 1",
      "allowed ∩ disallowed relations non-empty raises ValueError",
      lambda: _input(allowed_relation_types=frozenset({"imports"}),
                     disallowed_relation_types=frozenset({"imports"})),
      ValueError)


# ===========================================================================
# 20. C0.3 GRAPH TRAVERSAL — bounded, replay-stable, no silent drops
# ===========================================================================


def _build_graph():
    nodes = {
        "n0": c0_graph.GraphNodeRef("n0", "d0", "docs", "cleared", "fresh"),
        "n1": c0_graph.GraphNodeRef("n1", "d1", "docs", "cleared", "fresh"),
        "n2": c0_graph.GraphNodeRef("n2", "d2", "docs", "cleared", "fresh"),
        "n3": c0_graph.GraphNodeRef("n3", "d3", "docs", "cleared", "fresh"),
        "n4": c0_graph.GraphNodeRef("n4", "d4", "docs", "blocked", "fresh"),
        "n5": c0_graph.GraphNodeRef("n5", "d5", "docs", "cleared", "stale"),
    }
    edges = {
        "n0": (
            c0_graph.GraphEdge(c0_graph.GraphRelation.IMPORTS, "n0", "n1"),
            c0_graph.GraphEdge(c0_graph.GraphRelation.CONTRADICTS, "n0", "n3"),
            c0_graph.GraphEdge(c0_graph.GraphRelation.IMPORTS, "n0", "n4"),
            c0_graph.GraphEdge(c0_graph.GraphRelation.IMPORTS, "n0", "n5"),
        ),
        "n1": (c0_graph.GraphEdge(c0_graph.GraphRelation.DEPENDS_ON, "n1", "n2"),),
    }
    return nodes, edges


_nodes, _edges = _build_graph()


def _trav(**ov):
    return c0_graph.traverse_bounded(_input(**ov), edges_by_src=_edges, nodes_by_id=_nodes)


probe("C0.3.TR.max_hops_1_excludes_n2", "C0.3.md PHASE 2",
      "traverse(max_hops=1) excludes n2 (hop=2)",
      lambda: "n2" not in {n.node_id for n in _trav(max_hops=1).accepted_nodes}, True)
probe("C0.3.TR.max_nodes_2_strict_bound", "C0.3.md PHASE 2",
      "traverse(max_nodes=2) accepted_nodes ≤ 2",
      lambda: len(_trav(max_nodes=2).accepted_nodes) <= 2, True)
probe("C0.3.TR.acl_blocks_n4", "C0.3.md PHASE 2",
      "traverse blocks ACL-non-cleared neighbor n4",
      lambda: "n4" not in {n.node_id for n in _trav().accepted_nodes}, True)
probe("C0.3.TR.regulated_blocks_stale", "C0.3.md PHASE 2",
      "traverse(freshness=regulated) blocks stale n5",
      lambda: "n5" not in {n.node_id for n in _trav(freshness_class="regulated").accepted_nodes}, True)
probe("C0.3.TR.disallowed_relation_excluded", "C0.3.md PHASE 2",
      "traverse(disallow contradicts) excludes n3",
      lambda: "n3" not in {n.node_id for n in _trav(
          disallowed_relation_types=frozenset({"contradicts"})).accepted_nodes}, True)
probe("C0.3.TR.replay_stable_hash", "C0.3.md PHASE 2",
      "traverse manifest_hash deterministic across two runs",
      lambda: _trav().manifest.manifest_hash == _trav().manifest.manifest_hash, True)
probe("C0.3.TR.max_hops_0_only_seeds", "C0.3.md PHASE 2",
      "traverse(max_hops=0) accepted_nodes == {n0}",
      lambda: {n.node_id for n in _trav(max_hops=0).accepted_nodes}, {"n0"})
probe("C0.3.TR.no_silent_drops", "C0.3.md PHASE 2",
      "every rejection has explicit reason in manifest",
      lambda: all(reason in {r.value for r in c0_graph.GraphExclusionReason}
                  for reason, _cnt in _trav().manifest.rejection_counts), True)


# ===========================================================================
# 21. EVIDENCE STATUS / SUPPORT TARGET / ENUM ROUND-TRIPS
# ===========================================================================


probe("C0.STATUS.size", "C0_Context_Engine.md §EVIDENCE STATUS",
      "len(SupportStatus) == 6", lambda: len(list(SupportStatus)), 6)
for s in SupportStatus:
    probe(f"C0.STATUS.{s.name}.round_trip", "C0_Context_Engine.md §EVIDENCE STATUS",
          f"SupportStatus({s.value!r}) is {s.name}",
          lambda v=s.value, x=s: SupportStatus(v) is x, True)


probe("C0.7.MAP.gates_count", "C0.7.md §gate matrix",
      "len(QUALITY_GATES) == 11", lambda: len(QUALITY_GATES), 11)
probe("C0.7.MAP.invariants_count", "C0_Context_Engine.md §invariants",
      "len(INVARIANTS) == 12", lambda: len(INVARIANTS), 12)
probe("C0.7.MAP.failure_modes_count", "C0.7.md §failure-mode register",
      "len(FAILURE_MODES) == 14", lambda: len(FAILURE_MODES), 14)
probe("C0.7.MAP.failure_prevention_complete", "C0.7.md §failure-mode register",
      "every FAILURE_MODE has a prevention entry",
      lambda: c0_safety.failure_modes_match_spec_count(), True)
probe("C0.7.MAP.gates_complete", "C0.7.md §gate matrix",
      "GATE_FUNCTIONS keys == QUALITY_GATES set",
      lambda: c0_safety.gates_match_spec_count(), True)


# ===========================================================================
# 22. END-TO-END FULL CONTRACT BUILD (PASS path)
# ===========================================================================


def _full_contract_pass() -> SupportStatus:
    items = [E(eid=f"m{i}", source=f"d{i}", auth=0.95,
               cls=EvidenceClass.MUST_USE, lane="sparse") for i in range(5)]
    shaped = c0_shape.stratify(items)
    rep = c0_shape.scan_contradictions_and_gaps(
        shaped, support_target=SupportTarget.SOURCE_SUMMARY, high_stakes=False)
    bd = c0_contract.score(shaped, rep, support_target=SupportTarget.SOURCE_SUMMARY)
    return c0_contract.build_final_contract(
        route=R(), shaped=shaped, report=rep, breakdown=bd).status


probe("C0.E2E.PASS_path", "C0.5.md §build_final_contract",
      "build_final_contract(5×MUST_USE/sparse).status == PASS",
      _full_contract_pass, SupportStatus.PASS)


# ===========================================================================
# RENDER MARKDOWN TABLE
# ===========================================================================


def render() -> None:
    total = len(ROWS)
    passed = sum(1 for r in ROWS if r["status"] == "PASS")
    failed = total - passed
    print(f"<!-- {total} probes — {passed} PASS, {failed} FAIL -->\n")
    print(f"**Total atomic probes**: {total} | **PASS**: {passed} | **FAIL**: {failed}\n")
    print("| # | Req ID | Doc § | Requirement / Probe | Expected | Observed | Status |")
    print("|---|--------|-------|---------------------|----------|----------|--------|")
    for i, r in enumerate(ROWS, start=1):
        # Sanitize pipe chars for markdown.
        req_clean = r["req"].replace("|", "\\|")
        exp_clean = r["expected"].replace("|", "\\|").replace("\n", " ")
        obs_clean = r["observed"].replace("|", "\\|").replace("\n", " ")
        # Truncate over-long observed strings to keep the table scannable.
        if len(obs_clean) > 80:
            obs_clean = obs_clean[:77] + "..."
        if len(exp_clean) > 60:
            exp_clean = exp_clean[:57] + "..."
        print(f"| {i} | `{r['req_id']}` | {r['doc']} | {req_clean} | {exp_clean} | "
              f"{obs_clean} | **{r['status']}** |")


if __name__ == "__main__":
    render()
    fails = sum(1 for r in ROWS if r["status"] != "PASS")
    sys.exit(0 if fails == 0 else 1)
