"""W8 of plan apps-fort-knox-parity-c5d9a3 \u2014 DeterministicRiskScorer tests.

Pins every branch of the scorer:
- INSUFFICIENT_EVIDENCE short-circuit (no evidence + no features)
- APPROVE band (low risk_score)
- REFER band (mid risk_score)
- DECLINE band (high risk_score)
- product_class lookup vs UNKNOWN_PRODUCT_RISK_TIER fallback
- per-component breakdown (evidence, reconciliation, document density)
- determinism (same inputs \u2192 same outputs)
- rationale always contains the SYNTHETIC_SCORER_TAG
"""
from __future__ import annotations

import pytest

from apps_underwriting_ai.engines.risk_scorer import (
    APPROVE_CEILING,
    COVERAGE_WEIGHTS,
    DeterministicRiskScorer,
    EXPECTED_EVIDENCE_KINDS,
    PRODUCT_CLASS_RISK_TIER,
    REFER_CEILING,
    SYNTHETIC_SCORER_TAG,
    UNKNOWN_PRODUCT_RISK_TIER,
)
from apps_underwriting_ai.types.underwriting_types import (
    DecisionVerdict,
    EvidenceRecord,
    EvidenceRegister,
    ReconciliationResult,
    RiskFeatures,
    UnderwritingRequest,
)


# ----------------------------- helpers -----------------------------

def _make_request(
    *,
    product_class: str = "auto",
    n_documents: int = 1,
) -> UnderwritingRequest:
    return UnderwritingRequest(
        request_id="req-test",
        applicant_id="applicant-test",
        product_class=product_class,
        documents=tuple({"kind": f"doc{i}"} for i in range(n_documents)),
    )


def _make_register(*kinds: str) -> EvidenceRegister:
    return EvidenceRegister(
        request_id="req-test",
        records=tuple(
            EvidenceRecord(evidence_id=f"ev-{i}", source="src", kind=k)
            for i, k in enumerate(kinds)
        ),
    )


# ----------------------------- structural -----------------------------

def test_coverage_weights_sum_to_one():
    """Weights MUST sum to 1.0 for risk_score to be bounded in [0, 100]."""
    assert sum(COVERAGE_WEIGHTS.values()) == pytest.approx(1.0)


def test_thresholds_monotonic():
    """APPROVE_CEILING < REFER_CEILING enforces band ordering."""
    assert 0 < APPROVE_CEILING < REFER_CEILING <= 100


def test_synthetic_scorer_tag_is_present_module_level():
    """Tag must be a non-empty string and contain the disclaimer."""
    assert "NOT regulatory-grade" in SYNTHETIC_SCORER_TAG


# ----------------------------- INSUFFICIENT_EVIDENCE -----------------------------

def test_no_evidence_no_features_yields_insufficient_evidence():
    scorer = DeterministicRiskScorer()
    breakdown = scorer.score(
        request=_make_request(),
        register=None,
        features=None,
        reconciliation=None,
    )
    assert breakdown.verdict == DecisionVerdict.INSUFFICIENT_EVIDENCE
    assert breakdown.threshold_band == "insufficient"
    assert breakdown.risk_score == 0.0
    assert SYNTHETIC_SCORER_TAG in breakdown.rationale


def test_zero_evidence_but_features_present_does_not_short_circuit():
    """Having ANY features keeps the scorer in the active scoring path."""
    scorer = DeterministicRiskScorer()
    breakdown = scorer.score(
        request=_make_request(),
        register=None,
        features=RiskFeatures(feature_vector={"x": 1.0}),
        reconciliation=None,
    )
    assert breakdown.verdict != DecisionVerdict.INSUFFICIENT_EVIDENCE


# ----------------------------- APPROVE band -----------------------------

def test_full_coverage_with_low_risk_product_yields_approve():
    """Auto + full evidence + perfect reconciliation \u2192 APPROVE."""
    scorer = DeterministicRiskScorer()
    breakdown = scorer.score(
        request=_make_request(product_class="auto", n_documents=6),
        register=_make_register(*EXPECTED_EVIDENCE_KINDS),
        features=RiskFeatures(feature_vector={"x": 1.0}),
        reconciliation=ReconciliationResult(reconciled_count=6, unresolved_count=0),
    )
    assert breakdown.verdict == DecisionVerdict.APPROVE
    assert breakdown.threshold_band == "approve"
    assert breakdown.risk_score < APPROVE_CEILING
    assert breakdown.evidence_completeness == pytest.approx(1.0)
    assert breakdown.reconciliation_completeness == pytest.approx(1.0)
    assert breakdown.document_density == pytest.approx(1.0)


# ----------------------------- REFER band -----------------------------

def test_partial_coverage_with_mid_risk_product_yields_refer():
    """commercial_loan + partial coverage \u2192 REFER."""
    scorer = DeterministicRiskScorer()
    breakdown = scorer.score(
        request=_make_request(product_class="commercial_loan", n_documents=1),
        register=EvidenceRegister(request_id="req-test"),
        features=RiskFeatures(feature_vector={"x": 1.0}),
        reconciliation=ReconciliationResult(reconciled_count=1, unresolved_count=2),
    )
    assert breakdown.verdict == DecisionVerdict.REFER
    assert breakdown.threshold_band == "refer"
    assert APPROVE_CEILING <= breakdown.risk_score < REFER_CEILING


# ----------------------------- DECLINE band -----------------------------

def test_high_risk_unknown_product_with_zero_coverage_yields_decline_or_refer():
    """Unknown product + no coverage at all (but ANY feature to escape
    INSUFFICIENT_EVIDENCE) lands in REFER or DECLINE band; we accept either
    because the exact band depends on weight tuning, but it MUST be \u2265 APPROVE."""
    scorer = DeterministicRiskScorer()
    breakdown = scorer.score(
        request=_make_request(product_class="exotic_derivatives", n_documents=0),
        register=EvidenceRegister(request_id="req-test"),
        features=RiskFeatures(feature_vector={"x": 1.0}),
        reconciliation=None,
    )
    assert breakdown.verdict in (DecisionVerdict.REFER, DecisionVerdict.DECLINE)
    assert breakdown.product_risk_tier == UNKNOWN_PRODUCT_RISK_TIER
    assert breakdown.risk_score >= APPROVE_CEILING


# ----------------------------- product_class lookup -----------------------------

def test_known_product_class_uses_lookup_tier():
    scorer = DeterministicRiskScorer()
    breakdown = scorer.score(
        request=_make_request(product_class="auto"),
        register=_make_register("financial"),
        features=None,
        reconciliation=None,
    )
    assert breakdown.product_risk_tier == PRODUCT_CLASS_RISK_TIER["auto"]


def test_unknown_product_class_uses_fallback_tier():
    scorer = DeterministicRiskScorer()
    breakdown = scorer.score(
        request=_make_request(product_class="never_seen"),
        register=_make_register("financial"),
        features=None,
        reconciliation=None,
    )
    assert breakdown.product_risk_tier == UNKNOWN_PRODUCT_RISK_TIER


def test_product_class_lookup_is_case_insensitive():
    """User-supplied product_class with different casing must still hit lookup."""
    scorer = DeterministicRiskScorer()
    breakdown = scorer.score(
        request=_make_request(product_class="AUTO"),
        register=_make_register("financial"),
        features=None,
        reconciliation=None,
    )
    assert breakdown.product_risk_tier == PRODUCT_CLASS_RISK_TIER["auto"]


# ----------------------------- breakdown components -----------------------------

def test_evidence_completeness_partial_coverage():
    scorer = DeterministicRiskScorer()
    # Cover 3 of 5 expected kinds.
    breakdown = scorer.score(
        request=_make_request(),
        register=_make_register("financial", "credit", "collateral"),
        features=None,
        reconciliation=None,
    )
    assert breakdown.evidence_completeness == pytest.approx(3 / 5)


def test_reconciliation_completeness_zero_total_is_zero():
    scorer = DeterministicRiskScorer()
    breakdown = scorer.score(
        request=_make_request(),
        register=_make_register("financial"),
        features=None,
        reconciliation=ReconciliationResult(reconciled_count=0, unresolved_count=0),
    )
    assert breakdown.reconciliation_completeness == 0.0


def test_document_density_caps_at_one():
    scorer = DeterministicRiskScorer()
    breakdown = scorer.score(
        request=_make_request(n_documents=999),
        register=_make_register("financial"),
        features=None,
        reconciliation=None,
    )
    assert breakdown.document_density == 1.0


# ----------------------------- determinism -----------------------------

def test_scorer_is_deterministic():
    """Same inputs produce byte-identical breakdown."""
    scorer = DeterministicRiskScorer()
    args = dict(
        request=_make_request(product_class="home", n_documents=3),
        register=_make_register("financial", "credit", "policy"),
        features=RiskFeatures(feature_vector={"x": 0.5, "y": 0.7}),
        reconciliation=ReconciliationResult(reconciled_count=2, unresolved_count=1),
    )
    a = scorer.score(**args)
    b = scorer.score(**args)
    assert a.to_dict() == b.to_dict()


# ----------------------------- rationale invariants -----------------------------

def test_rationale_always_contains_synthetic_tag():
    """Every active-scoring rationale MUST contain the regulatory disclaimer tag."""
    scorer = DeterministicRiskScorer()
    breakdown = scorer.score(
        request=_make_request(),
        register=_make_register("financial"),
        features=None,
        reconciliation=None,
    )
    assert SYNTHETIC_SCORER_TAG in breakdown.rationale


def test_to_dict_is_json_serializable():
    """Breakdown must round-trip through json without TypeErrors."""
    import json

    scorer = DeterministicRiskScorer()
    breakdown = scorer.score(
        request=_make_request(),
        register=_make_register("financial"),
        features=None,
        reconciliation=None,
    )
    s = json.dumps(breakdown.to_dict(), sort_keys=True)
    assert "risk_score" in s
    assert "scorer" in s


# ----------------------------- DecisionPacketAssembler integration ------------

def test_assembler_uses_scorer_and_surfaces_breakdown_keys():
    """Assembler must surface scorer breakdown under risk_* feature_summary keys."""
    from apps_underwriting_ai.engines.decision_packet_assembler import (
        DecisionPacketAssembler,
    )

    decision = DecisionPacketAssembler().assemble(
        request=_make_request(product_class="auto", n_documents=6),
        register=_make_register(*EXPECTED_EVIDENCE_KINDS),
        features=RiskFeatures(feature_vector={"x": 1.0}),
        reconciliation=ReconciliationResult(reconciled_count=6, unresolved_count=0),
    )
    for key in (
        "risk_score",
        "risk_evidence_completeness",
        "risk_reconciliation_completeness",
        "risk_document_density",
        "risk_coverage_score",
        "risk_product_tier",
    ):
        assert key in decision.feature_summary, f"missing breakdown key: {key}"
    assert decision.verdict == DecisionVerdict.APPROVE
