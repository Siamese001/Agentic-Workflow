"""Tests for C0EvidenceContract (B05 — GAP-007, REQ-007/REQ-008).

Contract invariant tests:
- C0EvidenceContract is frozen
- All 6 fields required; validate() raises C0ContractViolation on any violation
- coverage_score outside [0,1] → violation
- abstain_hint=False with empty cited_spans → violation
- abstain_hint=True with empty cited_spans → valid (ABSTAIN path)
- non-CitedSpan in cited_spans → violation
- empty retrieval_id / request_id / evidence_hmac → violation

build() factory tests:
- coverage below threshold → abstain_hint=True
- coverage at or above threshold with spans → abstain_hint=False
- empty spans → abstain_hint=True regardless of coverage
- build() computes evidence_hmac deterministically
- build() raises C0ContractViolation on invalid inputs

HMAC tests:
- compute_hmac is deterministic for same inputs
- different spans → different HMAC
- HMAC verifiable from tuple alone

abstain_hint flag tests:
- abstain_hint=True → PA must emit ABSTAIN (structural check)
- cited_spans non-empty on non-ABSTAIN contracts

to_dict() contract:
- Contains all 6 keys
- cited_spans serialized as list of dicts
- coverage_score and abstain_hint preserved

Layer sovereignty:
- frozen dataclass raises FrozenInstanceError on mutation
"""

import pytest
from dataclasses import FrozenInstanceError

from agentic_core.L3_orchestration.types.c0_evidence_contract_types import (
    C0ContractViolation,
    C0EvidenceContract,
    CitedSpan,
    _ABSTAIN_COVERAGE_THRESHOLD,
)


def _span(span_id: str = "sp-1") -> CitedSpan:
    return CitedSpan(
        span_id=span_id,
        source_ref="doc://test.md",
        text_snippet="The river bank was muddy.",
        relevance_score=0.9,
        chunk_hash="abc123",
    )


def _valid_contract(**overrides) -> C0EvidenceContract:
    defaults = dict(
        retrieval_id="ret-001",
        request_id="req-001",
        coverage_score=0.85,
        abstain_hint=False,
        cited_spans=(_span(),),
        evidence_hmac="abcd1234efgh5678",
    )
    defaults.update(overrides)
    return C0EvidenceContract(**defaults)


class TestC0EvidenceContractValid:
    def test_valid_contract_passes_validate(self):
        _valid_contract().validate()

    def test_abstain_hint_true_empty_spans_passes(self):
        _valid_contract(abstain_hint=True, cited_spans=(), coverage_score=0.10).validate()

    def test_abstain_hint_true_with_spans_passes(self):
        _valid_contract(abstain_hint=True, cited_spans=(_span(),)).validate()

    def test_coverage_score_zero_with_abstain_passes(self):
        _valid_contract(abstain_hint=True, cited_spans=(), coverage_score=0.0).validate()

    def test_coverage_score_one_passes(self):
        _valid_contract(coverage_score=1.0).validate()


class TestC0EvidenceContractViolations:
    def test_empty_retrieval_id_raises(self):
        with pytest.raises(C0ContractViolation):
            _valid_contract(retrieval_id="").validate()

    def test_whitespace_retrieval_id_raises(self):
        with pytest.raises(C0ContractViolation):
            _valid_contract(retrieval_id="   ").validate()

    def test_empty_request_id_raises(self):
        with pytest.raises(C0ContractViolation):
            _valid_contract(request_id="").validate()

    def test_coverage_below_zero_raises(self):
        with pytest.raises(C0ContractViolation):
            _valid_contract(coverage_score=-0.01).validate()

    def test_coverage_above_one_raises(self):
        with pytest.raises(C0ContractViolation):
            _valid_contract(coverage_score=1.01).validate()

    def test_abstain_false_empty_spans_raises(self):
        with pytest.raises(C0ContractViolation):
            _valid_contract(abstain_hint=False, cited_spans=()).validate()

    def test_non_cited_span_in_spans_raises(self):
        with pytest.raises(C0ContractViolation):
            _valid_contract(cited_spans=({"not": "a span"},)).validate()

    def test_empty_evidence_hmac_raises(self):
        with pytest.raises(C0ContractViolation):
            _valid_contract(evidence_hmac="").validate()

    def test_c0_contract_violation_is_value_error_subclass(self):
        assert issubclass(C0ContractViolation, ValueError)


class TestBuildFactory:
    def test_build_low_coverage_sets_abstain_true(self):
        contract = C0EvidenceContract.build(
            retrieval_id="r1",
            request_id="req-1",
            coverage_score=_ABSTAIN_COVERAGE_THRESHOLD - 0.01,
            cited_spans=(_span(),),
        )
        assert contract.abstain_hint is True

    def test_build_high_coverage_with_spans_sets_abstain_false(self):
        contract = C0EvidenceContract.build(
            retrieval_id="r1",
            request_id="req-1",
            coverage_score=_ABSTAIN_COVERAGE_THRESHOLD + 0.10,
            cited_spans=(_span(),),
        )
        assert contract.abstain_hint is False

    def test_build_empty_spans_sets_abstain_true(self):
        contract = C0EvidenceContract.build(
            retrieval_id="r1",
            request_id="req-1",
            coverage_score=0.99,
            cited_spans=(),
        )
        assert contract.abstain_hint is True

    def test_build_computes_hmac(self):
        contract = C0EvidenceContract.build(
            retrieval_id="r1",
            request_id="req-1",
            coverage_score=0.80,
            cited_spans=(_span(),),
        )
        assert contract.evidence_hmac and len(contract.evidence_hmac) > 0

    def test_build_hmac_deterministic(self):
        spans = (_span("s1"), _span("s2"))
        h1 = C0EvidenceContract.compute_hmac(spans, "req-1")
        h2 = C0EvidenceContract.compute_hmac(spans, "req-1")
        assert h1 == h2

    def test_build_different_spans_different_hmac(self):
        span_a = CitedSpan(
            span_id="s1",
            source_ref="doc://a.md",
            text_snippet="aaa",
            relevance_score=0.9,
            chunk_hash="hash-aaa",
        )
        span_b = CitedSpan(
            span_id="s2",
            source_ref="doc://b.md",
            text_snippet="bbb",
            relevance_score=0.8,
            chunk_hash="hash-bbb",
        )
        h1 = C0EvidenceContract.compute_hmac((span_a,), "req-1")
        h2 = C0EvidenceContract.compute_hmac((span_b,), "req-1")
        assert h1 != h2

    def test_build_validates_on_creation(self):
        with pytest.raises(C0ContractViolation):
            C0EvidenceContract.build(
                retrieval_id="",
                request_id="req-1",
                coverage_score=0.80,
                cited_spans=(_span(),),
            )

    def test_build_at_exact_threshold_does_not_abstain(self):
        contract = C0EvidenceContract.build(
            retrieval_id="r-boundary",
            request_id="req-boundary",
            coverage_score=_ABSTAIN_COVERAGE_THRESHOLD,
            cited_spans=(_span(),),
        )
        assert contract.abstain_hint is False

    def test_build_just_below_threshold_abstains(self):
        contract = C0EvidenceContract.build(
            retrieval_id="r-below",
            request_id="req-below",
            coverage_score=_ABSTAIN_COVERAGE_THRESHOLD - 0.001,
            cited_spans=(_span(),),
        )
        assert contract.abstain_hint is True


class TestAbstainHintSemantics:
    def test_abstain_hint_preserved_in_contract(self):
        contract = _valid_contract(abstain_hint=True, cited_spans=())
        assert contract.abstain_hint is True

    def test_abstain_hint_false_requires_spans(self):
        contract = _valid_contract(abstain_hint=False, cited_spans=(_span(),))
        assert contract.abstain_hint is False
        assert len(contract.cited_spans) > 0


class TestToDictContract:
    def test_to_dict_contains_all_six_keys(self):
        d = _valid_contract().to_dict()
        assert "retrieval_id" in d
        assert "request_id" in d
        assert "coverage_score" in d
        assert "abstain_hint" in d
        assert "cited_spans" in d
        assert "evidence_hmac" in d

    def test_cited_spans_serialized_as_list_of_dicts(self):
        d = _valid_contract(cited_spans=(_span("s1"), _span("s2"))).to_dict()
        assert isinstance(d["cited_spans"], list)
        assert len(d["cited_spans"]) == 2
        assert "span_id" in d["cited_spans"][0]

    def test_abstain_hint_preserved_in_dict(self):
        d = _valid_contract(abstain_hint=False).to_dict()
        assert d["abstain_hint"] is False

    def test_coverage_score_preserved_in_dict(self):
        d = _valid_contract(coverage_score=0.77).to_dict()
        assert d["coverage_score"] == pytest.approx(0.77)


class TestLayerSovereignty:
    def test_frozen_contract_raises_on_mutation(self):
        contract = _valid_contract()
        with pytest.raises(FrozenInstanceError):
            contract.retrieval_id = "new-id"  # type: ignore[misc]

    def test_frozen_cited_spans_is_tuple(self):
        contract = _valid_contract()
        assert isinstance(contract.cited_spans, tuple)
