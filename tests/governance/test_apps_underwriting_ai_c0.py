"""W2.3 Governance tests — apps_underwriting_ai C0 evidence adapter.

Tests 40–44: 5 tests covering:
  - open_web_blocked is always True on all FinalEvidenceContract instances
  - PASS state emitted when all required document classes present, score >= 0.80
  - WEAK_WITH_CAVEATS emitted when contradictions detected
  - FAIL emitted when required documents missing and score < 0.40
  - FinalEvidenceContract carries all required fields (evidence_ids,
    coverage_map, contradiction_flags, support_score, evidence_sufficiency)

Plan: apps-underwriting-ai-spine-hardening-d7f3b2 W2.3.

All 5 tests pass immediately after W2.1/W2.2 implementation.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_underwriting_ai.integrations.underwriting_c0_adapter import (
    C0_STATE_FAIL,
    C0_STATE_PASS,
    C0_STATE_WEAK,
    OPEN_WEB_BLOCKED,
    FinalEvidenceContract,
    UnderwritingC0Adapter,
)

_adapter = UnderwritingC0Adapter()

_FULL_DOCS = [
    {
        "document_class": "BANK_STATEMENT",
        "average_monthly_balance": 8500.0,
        "account_tenure_months": 36,
        "overdraft_count_12m": 0,
        "deposit_consistency_score": 0.95,
    },
    {
        "document_class": "TAX_RETURN",
        "annual_gross_income": 95000.0,
        "tax_year": 2025,
        "filing_status": "single",
    },
    {
        "document_class": "CREDIT_REPORT",
        "credit_score": 740,
        "derogatory_mark_count": 0,
        "utilization_rate": 0.18,
        "inquiry_count_12m": 1,
    },
    {
        "document_class": "EMPLOYMENT_VERIFICATION",
        "employer_name": "Acme Corp",
        "employment_status": "EMPLOYED",
        "tenure_months": 48,
    },
]

_MISSING_DOCS = [
    {
        "document_class": "BANK_STATEMENT",
        "average_monthly_balance": 500.0,
        "account_tenure_months": 6,
    },
]

_CONTRADICTING_DOCS = [
    {
        "document_class": "BANK_STATEMENT",
        "average_monthly_balance": 200.0,
        "account_tenure_months": 12,
    },
    {
        "document_class": "TAX_RETURN",
        "annual_gross_income": 150000.0,
        "tax_year": 2025,
    },
    {
        "document_class": "CREDIT_REPORT",
        "credit_score": 730,
        "derogatory_mark_count": 4,
        "utilization_rate": 0.20,
    },
]


# ---------------------------------------------------------------------------
# Test 40 — open_web_blocked is always True
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_c0_open_web_blocked_is_always_true() -> None:
    """FinalEvidenceContract.open_web_blocked must always be True.

    The SUBMITTED_DOCUMENT_EVIDENCE_ONLY mode enforces that no open-web
    retrieval is ever attempted. This invariant is verified on all three
    c0_state outcomes.
    """
    fec_pass = _adapter.run(_FULL_DOCS, demo_policy_hash="policy-hash-v1")
    fec_weak = _adapter.run(_CONTRADICTING_DOCS, demo_policy_hash="policy-hash-v1")
    fec_fail = _adapter.run([], demo_policy_hash="policy-hash-v1")

    assert fec_pass.open_web_blocked is True, (
        "FinalEvidenceContract.open_web_blocked must be True on PASS state. "
        "C0 mode SUBMITTED_DOCUMENT_EVIDENCE_ONLY never accesses open web."
    )
    assert fec_weak.open_web_blocked is True, (
        "FinalEvidenceContract.open_web_blocked must be True on WEAK state."
    )
    assert fec_fail.open_web_blocked is True, (
        "FinalEvidenceContract.open_web_blocked must be True on FAIL state."
    )
    assert OPEN_WEB_BLOCKED is True, (
        "Module-level OPEN_WEB_BLOCKED constant must be True."
    )


# ---------------------------------------------------------------------------
# Test 41 — PASS state when all required documents present
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_c0_pass_state_when_all_required_documents_present() -> None:
    """C0 adapter must emit PASS when all 3 required document classes present
    and no contradictions detected.

    Required classes: BANK_STATEMENT, TAX_RETURN, CREDIT_REPORT.
    PASS threshold: support_score >= 0.80.
    """
    fec = _adapter.run(_FULL_DOCS, demo_policy_hash="policy-hash-v1")

    assert fec.c0_state == C0_STATE_PASS, (
        f"Expected c0_state=PASS with all required documents, got {fec.c0_state!r}. "
        f"support_score={fec.support_score}, missing={fec.missing_evidence_flags}, "
        f"contradictions={fec.contradiction_flags}"
    )
    assert fec.support_score >= 0.80, (
        f"PASS state requires support_score >= 0.80, got {fec.support_score}."
    )
    assert fec.missing_evidence_flags == [], (
        f"PASS state must have no missing required classes, got {fec.missing_evidence_flags}."
    )
    assert fec.contradiction_flags == [], (
        f"PASS state must have no contradiction flags, got {fec.contradiction_flags}."
    )
    assert fec.evidence_sufficiency == "sufficient", (
        f"PASS state must have evidence_sufficiency='sufficient', got {fec.evidence_sufficiency!r}."
    )


# ---------------------------------------------------------------------------
# Test 42 — WEAK state when contradictions detected
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_c0_weak_state_when_contradictions_detected() -> None:
    """C0 adapter must emit WEAK_WITH_CAVEATS when cross-field contradictions
    are detected, even when all required document classes are present.

    Contradiction: credit_score=730 with derogatory_mark_count=4 triggers
    CREDIT_SCORE_DEROGATORY_MISMATCH rule.
    Contradiction: income=150000 with balance=200 triggers INCOME_BALANCE_MISMATCH.
    """
    fec = _adapter.run(_CONTRADICTING_DOCS, demo_policy_hash="policy-hash-v1")

    assert fec.c0_state == C0_STATE_WEAK, (
        f"Expected c0_state=WEAK_WITH_CAVEATS with contradicting documents, "
        f"got {fec.c0_state!r}. contradiction_flags={fec.contradiction_flags}"
    )
    assert len(fec.contradiction_flags) > 0, (
        "WEAK state due to contradiction must have at least one contradiction_flag."
    )
    assert fec.evidence_sufficiency == "partial", (
        f"WEAK state must have evidence_sufficiency='partial', got {fec.evidence_sufficiency!r}."
    )
    assert fec.open_web_blocked is True


# ---------------------------------------------------------------------------
# Test 43 — FAIL state when required documents missing and score low
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_c0_fail_state_when_required_documents_missing() -> None:
    """C0 adapter must emit FAIL when required document classes are absent
    and support_score falls below the WEAK threshold (0.40).

    Empty submission must always be FAIL with all required classes flagged as missing.
    """
    fec_empty = _adapter.run([], demo_policy_hash="policy-hash-v1")
    fec_partial = _adapter.run(_MISSING_DOCS, demo_policy_hash="policy-hash-v1")

    assert fec_empty.c0_state == C0_STATE_FAIL, (
        f"Empty submission must be c0_state=FAIL, got {fec_empty.c0_state!r}."
    )
    # Hardening update: missing-evidence flags use the structured
    # "MISSING_DOC:<CLASS>" form so the contract can also express
    # "MISSING_FIELD:<CLASS>.<field>" without ambiguity.
    assert set(fec_empty.missing_evidence_flags) == {
        "MISSING_DOC:BANK_STATEMENT",
        "MISSING_DOC:TAX_RETURN",
        "MISSING_DOC:CREDIT_REPORT",
    }, (
        f"Empty submission must flag all required classes missing, "
        f"got {fec_empty.missing_evidence_flags}."
    )
    assert fec_empty.support_score == 0.0, (
        f"Empty submission must have support_score=0.0, got {fec_empty.support_score}."
    )
    assert fec_empty.evidence_sufficiency == "insufficient", (
        f"FAIL state must have evidence_sufficiency='insufficient', "
        f"got {fec_empty.evidence_sufficiency!r}."
    )

    assert fec_partial.c0_state == C0_STATE_FAIL, (
        f"Single-document submission missing TAX_RETURN and CREDIT_REPORT must be FAIL, "
        f"got {fec_partial.c0_state!r}. support_score={fec_partial.support_score}"
    )
    assert "MISSING_DOC:TAX_RETURN" in fec_partial.missing_evidence_flags
    assert "MISSING_DOC:CREDIT_REPORT" in fec_partial.missing_evidence_flags


# ---------------------------------------------------------------------------
# Test 44 — FinalEvidenceContract carries all required fields
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_c0_final_evidence_contract_carries_all_required_fields() -> None:
    """FinalEvidenceContract must carry all required fields for the PA
    compiler slot C0 and the Exit FEC producer.

    Required fields per W2.2 spec:
      c0_mode, c0_state, open_web_blocked, evidence_contract_id,
      evidence_ids, document_coverage_map, extracted_span_map,
      contradiction_flags, missing_evidence_flags, support_score,
      evidence_sufficiency, demo_policy_hash, document_count,
      required_classes_present, optional_classes_present.
    """
    fec = _adapter.run(_FULL_DOCS, demo_policy_hash="fixture-policy-abc123")

    assert fec.c0_mode == "SUBMITTED_DOCUMENT_EVIDENCE_ONLY", (
        f"c0_mode must be SUBMITTED_DOCUMENT_EVIDENCE_ONLY, got {fec.c0_mode!r}."
    )
    assert isinstance(fec.evidence_contract_id, str) and fec.evidence_contract_id.startswith("fec-"), (
        f"evidence_contract_id must be a 'fec-...' string, got {fec.evidence_contract_id!r}."
    )
    assert isinstance(fec.evidence_ids, list), "evidence_ids must be a list."
    assert len(fec.evidence_ids) > 0, (
        "evidence_ids must be non-empty when documents with recognized fields are submitted."
    )
    assert isinstance(fec.document_coverage_map, dict), "document_coverage_map must be a dict."
    assert isinstance(fec.extracted_span_map, dict), "extracted_span_map must be a dict."
    assert isinstance(fec.contradiction_flags, list), "contradiction_flags must be a list."
    assert isinstance(fec.missing_evidence_flags, list), "missing_evidence_flags must be a list."
    assert isinstance(fec.support_score, float), "support_score must be a float."
    assert 0.0 <= fec.support_score <= 1.0, (
        f"support_score must be in [0.0, 1.0], got {fec.support_score}."
    )
    assert fec.evidence_sufficiency in ("sufficient", "partial", "insufficient"), (
        f"evidence_sufficiency must be one of sufficient/partial/insufficient, "
        f"got {fec.evidence_sufficiency!r}."
    )
    assert fec.demo_policy_hash == "fixture-policy-abc123", (
        f"demo_policy_hash must be preserved from input, got {fec.demo_policy_hash!r}."
    )
    assert isinstance(fec.document_count, int) and fec.document_count == len(_FULL_DOCS), (
        f"document_count must equal len(submitted_documents), got {fec.document_count}."
    )
    assert isinstance(fec.required_classes_present, list), "required_classes_present must be a list."
    assert isinstance(fec.optional_classes_present, list), "optional_classes_present must be a list."

    fec_dict = fec.to_dict()
    for key in (
        "c0_mode", "c0_state", "open_web_blocked", "evidence_contract_id",
        "evidence_ids", "document_coverage_map", "extracted_span_map",
        "contradiction_flags", "missing_evidence_flags", "support_score",
        "evidence_sufficiency", "demo_policy_hash", "document_count",
        "required_classes_present", "optional_classes_present",
    ):
        assert key in fec_dict, f"to_dict() missing required field '{key}'."
