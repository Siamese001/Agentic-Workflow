"""Type-contract tests for apps_underwriting_ai.

Validates frozen-dataclass discipline and DecisionVerdict enum bounds.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from apps_underwriting_ai.types.underwriting_types import (
    DecisionPacket,
    DecisionVerdict,
    EvidenceRecord,
    EvidenceRegister,
    ReconciliationResult,
    RiskFeatures,
    UnderwritingRequest,
    UnderwritingResult,
)


# -- DecisionVerdict enum bounds ---------------------------------------------


def test_decision_verdict_has_exactly_four_members() -> None:
    assert len(DecisionVerdict) == 4


def test_decision_verdict_members_are_str_subclass() -> None:
    for v in DecisionVerdict:
        assert isinstance(v.value, str)


def test_decision_verdict_member_values() -> None:
    assert DecisionVerdict.APPROVE.value == "approve"
    assert DecisionVerdict.DECLINE.value == "decline"
    assert DecisionVerdict.REFER.value == "refer"
    assert DecisionVerdict.INSUFFICIENT_EVIDENCE.value == "insufficient_evidence"


# -- UnderwritingRequest frozen discipline -----------------------------------


def test_underwriting_request_is_frozen() -> None:
    req = UnderwritingRequest(
        request_id="t-1", applicant_id="a-1", product_class="auto"
    )
    with pytest.raises(FrozenInstanceError):
        req.request_id = "t-2"  # type: ignore[misc]


def test_underwriting_request_documents_default_is_tuple() -> None:
    req = UnderwritingRequest(
        request_id="t-1", applicant_id="a-1", product_class="auto"
    )
    assert isinstance(req.documents, tuple)
    assert req.documents == ()


def test_underwriting_request_metadata_default_is_dict() -> None:
    req = UnderwritingRequest(
        request_id="t-1", applicant_id="a-1", product_class="auto"
    )
    assert isinstance(req.metadata, dict)
    assert req.metadata == {}


# -- EvidenceRegister immutability -------------------------------------------


def test_evidence_register_records_default_is_tuple() -> None:
    reg = EvidenceRegister(request_id="r-1")
    assert isinstance(reg.records, tuple)
    assert reg.records == ()


def test_evidence_register_is_frozen() -> None:
    reg = EvidenceRegister(request_id="r-1")
    with pytest.raises(FrozenInstanceError):
        reg.request_id = "r-2"  # type: ignore[misc]


def test_evidence_record_is_frozen() -> None:
    rec = EvidenceRecord(evidence_id="e-1", source="src", kind="financial")
    with pytest.raises(FrozenInstanceError):
        rec.evidence_id = "e-2"  # type: ignore[misc]


# -- ReconciliationResult ----------------------------------------------------


def test_reconciliation_result_defaults() -> None:
    r = ReconciliationResult()
    assert r.reconciled_count == 0
    assert r.unresolved_count == 0
    assert isinstance(r.notes, tuple)
    assert r.notes == ()


def test_reconciliation_result_is_frozen() -> None:
    r = ReconciliationResult(reconciled_count=2)
    with pytest.raises(FrozenInstanceError):
        r.reconciled_count = 5  # type: ignore[misc]


# -- RiskFeatures ------------------------------------------------------------


def test_risk_features_defaults() -> None:
    f = RiskFeatures()
    assert f.feature_vector == {}
    assert f.derived_at == ""
    assert f.notes == ()


def test_risk_features_is_frozen() -> None:
    f = RiskFeatures(feature_vector={"x": 1.0})
    with pytest.raises(FrozenInstanceError):
        f.derived_at = "now"  # type: ignore[misc]


# -- DecisionPacket ----------------------------------------------------------


def test_decision_packet_required_fields() -> None:
    d = DecisionPacket(request_id="r-1", verdict=DecisionVerdict.APPROVE)
    assert d.request_id == "r-1"
    assert d.verdict == DecisionVerdict.APPROVE
    assert d.rationale == ""
    assert d.evidence_refs == ()
    assert d.feature_summary == {}
    assert d.gate_violations == ()


def test_decision_packet_is_frozen() -> None:
    d = DecisionPacket(request_id="r-1", verdict=DecisionVerdict.APPROVE)
    with pytest.raises(FrozenInstanceError):
        d.verdict = DecisionVerdict.DECLINE  # type: ignore[misc]


# -- UnderwritingResult ------------------------------------------------------


def test_underwriting_result_required_fields() -> None:
    decision = DecisionPacket(
        request_id="r-1", verdict=DecisionVerdict.INSUFFICIENT_EVIDENCE
    )
    register = EvidenceRegister(request_id="r-1")
    features = RiskFeatures()
    reconciliation = ReconciliationResult()
    result = UnderwritingResult(
        request_id="r-1",
        decision=decision,
        register=register,
        features=features,
        reconciliation=reconciliation,
    )
    assert result.request_id == "r-1"
    assert result.trace_id == ""


def test_underwriting_result_is_frozen() -> None:
    decision = DecisionPacket(
        request_id="r-1", verdict=DecisionVerdict.INSUFFICIENT_EVIDENCE
    )
    register = EvidenceRegister(request_id="r-1")
    features = RiskFeatures()
    reconciliation = ReconciliationResult()
    result = UnderwritingResult(
        request_id="r-1",
        decision=decision,
        register=register,
        features=features,
        reconciliation=reconciliation,
    )
    with pytest.raises(FrozenInstanceError):
        result.trace_id = "trace-x"  # type: ignore[misc]
