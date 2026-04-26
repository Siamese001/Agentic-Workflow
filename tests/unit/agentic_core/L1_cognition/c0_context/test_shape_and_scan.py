"""Tests for C0.4 shape + C0.4A contradiction/gap scan."""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.c0_context.shape_and_scan import (
    compress_to_budget,
    dedupe,
    scan_contradictions_and_gaps,
    stratify,
)
from agentic_core.L1_cognition.c0_context.types import (
    ContradictionType,
    EvidenceClass,
    EvidenceItem,
    GapType,
    SupportTarget,
)


def _ev(
    eid: str,
    *,
    source: str = "doc:a",
    span: str = "L1",
    auth: float = 0.6,
    cls: EvidenceClass = EvidenceClass.SUPPORTING,
    lane: str = "dense",
    fresh: str = "fresh",
    source_class: str = "docs",
    cost: int = 10,
    acl: str = "cleared",
) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=eid,
        source_id=source,
        source_class=source_class,
        span_ref=span,
        quote_or_summary="...",
        retrieval_lane=lane,
        authority_score=auth,
        freshness_status=fresh,
        acl_status=acl,
        token_cost=cost,
        evidence_class=cls,
    )


# ---------- DEDUPE ----------


def test_dedupe_collapses_same_source_span() -> None:
    a = _ev("a", source="d:1", span="L10", auth=0.5)
    b = _ev("b", source="d:1", span="L10", auth=0.9)
    c = _ev("c", source="d:1", span="L11", auth=0.7)
    out = dedupe([a, b, c])
    assert len(out) == 2
    # Highest authority wins
    by_span = {x.span_ref: x for x in out}
    assert by_span["L10"].evidence_id == "b"


def test_dedupe_empty_input() -> None:
    assert dedupe([]) == []


# ---------- STRATIFY ----------


def test_stratify_by_authority() -> None:
    items = [
        _ev("a", auth=0.95),  # MUST_USE
        _ev("b", auth=0.6),   # SUPPORTING
        _ev("c", auth=0.3),   # BACKGROUND
        _ev("d", auth=0.1),   # EXCLUDED
    ]
    out = stratify(items)
    ids = lambda bucket: {x.evidence_id for x in bucket}
    assert ids(out.must_use) == {"a"}
    assert ids(out.supporting) == {"b"}
    assert ids(out.background) == {"c"}
    assert {x.evidence_id for x, _r in out.excluded} == {"d"}


def test_stratify_honors_prelabeled_classes() -> None:
    items = [
        _ev("c", cls=EvidenceClass.CONTRADICTS, auth=0.9),
        _ev("d", cls=EvidenceClass.DEFINITIONS),
        _ev("l", cls=EvidenceClass.LINEAGE),
    ]
    out = stratify(items)
    assert {x.evidence_id for x in out.contradicts} == {"c"}
    assert {x.evidence_id for x in out.definitions} == {"d"}
    assert {x.evidence_id for x in out.lineage} == {"l"}


def test_stratify_token_estimate_sum() -> None:
    items = [_ev("a", auth=0.9, cost=10), _ev("b", auth=0.6, cost=20)]
    out = stratify(items)
    assert out.token_estimate == 30


# ---------- COMPRESS ----------


def test_compress_trims_background_first() -> None:
    items = [
        _ev("m", auth=0.95, cost=30),  # must_use
        _ev("s", auth=0.6, cost=20),   # supporting
        _ev("b1", auth=0.3, cost=20),  # background
        _ev("b2", auth=0.3, cost=20),  # background
    ]
    shaped = stratify(items)
    out = compress_to_budget(shaped, max_token_context=60)
    # must_use + supporting = 50; only one background fits
    assert len(out.background) <= 1
    assert len(out.must_use) == 1
    assert len(out.supporting) == 1


def test_compress_raises_when_must_use_exceeds_budget() -> None:
    items = [_ev("m", auth=0.95, cost=200)]
    shaped = stratify(items)
    with pytest.raises(ValueError, match="must-keep"):
        compress_to_budget(shaped, max_token_context=50)


def test_compress_invalid_budget_raises() -> None:
    shaped = stratify([_ev("a", auth=0.9)])
    with pytest.raises(ValueError):
        compress_to_budget(shaped, max_token_context=0)


# ---------- SCAN CONTRADICTIONS + GAPS ----------


def test_scan_emits_contradiction_flag_when_contradicts_present() -> None:
    items = [
        _ev("m", auth=0.9, cls=EvidenceClass.MUST_USE),
        _ev("c", auth=0.8, cls=EvidenceClass.CONTRADICTS, source="doc:b"),
    ]
    shaped = stratify(items)
    report = scan_contradictions_and_gaps(
        shaped, support_target=SupportTarget.SOURCE_SUMMARY, high_stakes=False,
    )
    assert len(report.contradiction_flags) == 1
    assert report.contradiction_flags[0].source_a == "doc:b"


def test_scan_no_contradiction_no_flag() -> None:
    shaped = stratify([_ev("a", auth=0.9)])
    report = scan_contradictions_and_gaps(
        shaped, support_target=SupportTarget.SOURCE_SUMMARY, high_stakes=False,
    )
    assert report.contradiction_flags == ()


def test_scan_missing_exact_quote_gap() -> None:
    items = [_ev("a", auth=0.9, lane="dense")]  # no sparse/hybrid
    shaped = stratify(items)
    report = scan_contradictions_and_gaps(
        shaped, support_target=SupportTarget.EXACT_QUOTE, high_stakes=False,
    )
    assert any(g.gap_type == GapType.MISSING_EXACT_QUOTE for g in report.unresolved_gaps)


def test_scan_exact_quote_satisfied_by_sparse() -> None:
    items = [_ev("a", auth=0.9, lane="sparse")]
    shaped = stratify(items)
    report = scan_contradictions_and_gaps(
        shaped, support_target=SupportTarget.EXACT_QUOTE, high_stakes=False,
    )
    assert not any(g.gap_type == GapType.MISSING_EXACT_QUOTE for g in report.unresolved_gaps)


def test_scan_missing_direct_support_gap_when_only_supporting() -> None:
    items = [_ev("a", auth=0.6)]  # SUPPORTING tier
    shaped = stratify(items)
    report = scan_contradictions_and_gaps(
        shaped, support_target=SupportTarget.SOURCE_SUMMARY, high_stakes=False,
    )
    assert any(g.gap_type == GapType.MISSING_DIRECT_SUPPORT for g in report.unresolved_gaps)


def test_scan_empty_evidence_emits_severe_gap() -> None:
    shaped = stratify([])
    report = scan_contradictions_and_gaps(
        shaped, support_target=SupportTarget.SOURCE_SUMMARY, high_stakes=False,
    )
    severe = [g for g in report.unresolved_gaps if g.severity >= 0.9]
    assert any(g.gap_type == GapType.MISSING_DIRECT_SUPPORT for g in severe)


def test_scan_high_stakes_single_source_gap() -> None:
    items = [
        _ev("a", auth=0.9, source="doc:x"),
        _ev("b", auth=0.9, source="doc:x"),  # same source
    ]
    shaped = stratify(items)
    report = scan_contradictions_and_gaps(
        shaped, support_target=SupportTarget.POLICY_CLAUSE, high_stakes=True,
    )
    assert any(g.gap_type == GapType.MISSING_SOURCE_DIVERSITY for g in report.unresolved_gaps)


def test_scan_acl_uncleared_emits_gap() -> None:
    items = [_ev("a", auth=0.95, acl="pending")]
    shaped = stratify(items)
    report = scan_contradictions_and_gaps(
        shaped, support_target=SupportTarget.SOURCE_SUMMARY, high_stakes=False,
    )
    assert any(g.gap_type == GapType.MISSING_TENANT_ACL_PROOF for g in report.unresolved_gaps)


def test_scan_contradiction_type_inferred_for_code_vs_docs() -> None:
    anchor = _ev("m", auth=0.9, cls=EvidenceClass.MUST_USE, source_class="docs")
    contra = _ev("c", auth=0.8, cls=EvidenceClass.CONTRADICTS, source_class="code", source="x")
    shaped = stratify([anchor, contra])
    report = scan_contradictions_and_gaps(
        shaped, support_target=SupportTarget.SOURCE_SUMMARY, high_stakes=False,
    )
    assert report.contradiction_flags[0].contradiction_type == ContradictionType.CODE
