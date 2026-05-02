"""End-to-end contract tests for apps_underwriting_ai.

Validates pipeline-level invariants — every APPROVE has evidence, every
unresolved-reconciliation forces REFER, request_id is preserved end-to-end,
trace_id propagates, gate_violations is always a tuple.
"""

from __future__ import annotations

from apps_underwriting_ai.engines.decision_packet_assembler import (
    DecisionPacketAssembler,
)
from apps_underwriting_ai.engines.underwriting_engine import UnderwritingEngine
from apps_underwriting_ai.types.underwriting_types import (
    DecisionVerdict,
    EvidenceRegister,
    ReconciliationResult,
    RiskFeatures,
    UnderwritingRequest,
)


def _request_with_docs(n: int) -> UnderwritingRequest:
    return UnderwritingRequest(
        request_id=f"contract-{n}",
        applicant_id="contract-applicant",
        product_class="auto",
        documents=tuple({"kind": f"doc_{i}"} for i in range(n)),
    )


# -- Invariant 1: every APPROVE has ≥1 evidence record -----------------------


def test_approve_implies_nonempty_evidence_register() -> None:
    result = UnderwritingEngine().run(_request_with_docs(2))
    if result.decision.verdict == DecisionVerdict.APPROVE:
        assert len(result.register.records) >= 1


# -- Invariant 2: unresolved reconciliations push risk_score toward REFER ----
# Updated 2026-05-02 (plan apps-fort-knox-parity-c5d9a3 W8): the verdict logic
# now delegates to DeterministicRiskScorer. Unresolved documents reduce
# reconciliation_completeness, which raises risk_score. A high-baseline
# product class plus low coverage reliably crosses the REFER ceiling.


def test_unresolved_reconciliation_forces_refer() -> None:
    # commercial_loan baseline tier (60) + low coverage (no evidence,
    # 1/3 reconciliation, 1/6 document density) must cross APPROVE_CEILING=35
    # into the REFER band.
    from apps_underwriting_ai.types.underwriting_types import UnderwritingRequest

    request = UnderwritingRequest(
        request_id="req-refer-001",
        applicant_id="applicant-1",
        product_class="commercial_loan",
        documents=({"kind": "tax_return"},),
    )
    register = EvidenceRegister(request_id=request.request_id)
    features = RiskFeatures(feature_vector={"x": 1.0})
    reconciliation = ReconciliationResult(
        reconciled_count=1, unresolved_count=2, notes=("synthetic",)
    )
    decision = DecisionPacketAssembler().assemble(
        request=request,
        register=register,
        features=features,
        reconciliation=reconciliation,
    )
    assert decision.verdict == DecisionVerdict.REFER
    # Rationale must surface the reconciliation_completeness contribution
    # so the unresolved count's impact on the verdict is auditable.
    assert "reconciliation=" in decision.rationale
    # And the breakdown must be in feature_summary for downstream audit.
    assert decision.feature_summary["risk_reconciliation_completeness"] < 1.0


# -- Invariant 3: empty evidence + empty features → INSUFFICIENT_EVIDENCE ----


def test_empty_state_yields_insufficient_evidence() -> None:
    request = _request_with_docs(0)
    register = EvidenceRegister(request_id=request.request_id)
    features = RiskFeatures()  # empty vector
    reconciliation = ReconciliationResult()
    decision = DecisionPacketAssembler().assemble(
        request=request,
        register=register,
        features=features,
        reconciliation=reconciliation,
    )
    assert decision.verdict == DecisionVerdict.INSUFFICIENT_EVIDENCE


# -- Invariant 4: request_id preserved end-to-end ---------------------------


def test_request_id_preserved() -> None:
    for n in (0, 1, 5):
        request = _request_with_docs(n)
        result = UnderwritingEngine().run(request)
        assert result.request_id == request.request_id
        assert result.decision.request_id == request.request_id
        assert result.register.request_id == request.request_id


# -- Invariant 5: trace_id propagates through the pipeline -------------------


def test_trace_id_propagates() -> None:
    request = _request_with_docs(1)
    result = UnderwritingEngine().run(request, trace_id="trace-contract-001")
    assert result.trace_id == "trace-contract-001"


def test_trace_id_default_is_empty() -> None:
    request = _request_with_docs(1)
    result = UnderwritingEngine().run(request)
    assert result.trace_id == ""


# -- Invariant 6: gate_violations is always a tuple --------------------------


def test_gate_violations_is_always_tuple() -> None:
    for n in (0, 1, 3):
        result = UnderwritingEngine().run(_request_with_docs(n))
        assert isinstance(result.decision.gate_violations, tuple)


# -- Invariant 7: verdict is always one of the four enum members -------------


def test_verdict_always_in_enum() -> None:
    valid = set(DecisionVerdict)
    for n in (0, 1, 2, 5, 10):
        result = UnderwritingEngine().run(_request_with_docs(n))
        assert result.decision.verdict in valid


# -- Invariant 8: reconciled_count tracks documents (skeleton-stage) ---------


def test_reconciled_count_matches_document_count() -> None:
    for n in (0, 1, 3, 5):
        result = UnderwritingEngine().run(_request_with_docs(n))
        assert result.reconciliation.reconciled_count == n
        assert result.reconciliation.unresolved_count == 0


# -- Invariant 9: feature_vector contains skeleton-stage canonical keys ------


def test_feature_vector_canonical_keys() -> None:
    result = UnderwritingEngine().run(_request_with_docs(2))
    assert "document_count" in result.features.feature_vector
    assert "reconciled_count" in result.features.feature_vector
    assert "unresolved_count" in result.features.feature_vector


# -- Invariant 10: evidence_register grows by exactly 5 records --------------


def test_evidence_register_grows_by_five() -> None:
    """Stage 4 collects across 5 dimensions; register should have exactly 5 records."""
    result = UnderwritingEngine().run(_request_with_docs(1))
    assert len(result.register.records) == 5
    kinds = {r.kind for r in result.register.records}
    assert kinds == {"financial", "credit", "collateral", "relationship", "policy"}
