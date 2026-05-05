"""W3.4 Governance tests — apps_underwriting_ai L3/L2 workflow adapters.

8 tests covering:
  45 — L3 expands, never executes (l3_expanded=True; no stage payload returned)
  46 — L3 injects evidence_refs into requires_evidence_refs stages only
  47 — L3 HITL posture: HITL_REQUIRED on missing required documents
  48 — L3 HITL posture: HITL_ADVISORY on borderline score band [0.40, 0.55)
  49 — L3 HITL posture: HITL_NONE on clean PASS FEC
  50 — L2 adapters each emit exactly one receipt with no_retrieval=True, no_l4_write=True
  51 — L2 feature derivation requires evidence_refs from reconciliation result
  52 — L2 decision assembly verdict + reason_codes are locked (immutable intent)

Plan: apps-underwriting-ai-spine-hardening-d7f3b2 W3.4.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_underwriting_ai.integrations.underwriting_l3_workflow_adapter import (
    HITL_ADVISORY,
    HITL_NONE,
    HITL_REQUIRED,
    ROUTE_FAMILY,
    STAGE_COUNT,
    UnderwritingL3WorkflowAdapter,
    WorkflowExpansion,
    _resolve_hitl_posture,
)
from apps_underwriting_ai.integrations.underwriting_l2_step_adapters import (
    ALL_ADAPTERS,
    L2_RECEIPT_E1,
    L2_RECEIPT_E2,
    L2_RECEIPT_E3,
    L2_RECEIPT_E5,
    DecisionAssemblyAdapter,
    DocumentReconciliationAdapter,
    EvidenceRegisterAdapter,
    FeatureDerivationAdapter,
    RiskScoringAdapter,
)

_l3 = UnderwritingL3WorkflowAdapter()

# ---------------------------------------------------------------------------
# Shared FEC fixtures
# ---------------------------------------------------------------------------

def _fec_pass(evidence_ids: list[str] | None = None) -> dict[str, Any]:
    return {
        "c0_mode": "SUBMITTED_DOCUMENT_EVIDENCE_ONLY",
        "c0_state": "PASS",
        "open_web_blocked": True,
        "evidence_contract_id": "fec-pass-abc",
        "evidence_ids": evidence_ids or ["ev-BANK_STATEMENT-001", "ev-TAX_RETURN-002", "ev-CREDIT_REPORT-003"],
        "document_coverage_map": {"BANK_STATEMENT": True, "TAX_RETURN": True, "CREDIT_REPORT": True},
        "extracted_span_map": {
            "ev-BANK_STATEMENT-001": {"document_class": "BANK_STATEMENT", "field_name": "average_monthly_balance", "value": 8500.0, "confidence": 0.9},
            "ev-TAX_RETURN-002": {"document_class": "TAX_RETURN", "field_name": "annual_gross_income", "value": 95000.0, "confidence": 0.9},
            "ev-CREDIT_REPORT-003": {"document_class": "CREDIT_REPORT", "field_name": "credit_score", "value": 740, "confidence": 0.95},
        },
        "contradiction_flags": [],
        "missing_evidence_flags": [],
        "support_score": 0.85,
        "evidence_sufficiency": "sufficient",
        "demo_policy_hash": "policy-hash-v1",
        "document_count": 3,
        "required_classes_present": ["BANK_STATEMENT", "TAX_RETURN", "CREDIT_REPORT"],
        "optional_classes_present": [],
    }


def _fec_fail_missing() -> dict[str, Any]:
    return {
        "c0_mode": "SUBMITTED_DOCUMENT_EVIDENCE_ONLY",
        "c0_state": "FAIL",
        "open_web_blocked": True,
        "evidence_contract_id": "fec-fail-xyz",
        "evidence_ids": [],
        "document_coverage_map": {},
        "extracted_span_map": {},
        "contradiction_flags": [],
        "missing_evidence_flags": ["TAX_RETURN", "CREDIT_REPORT"],
        "support_score": 0.0,
        "evidence_sufficiency": "insufficient",
        "demo_policy_hash": "policy-hash-v1",
        "document_count": 1,
        "required_classes_present": ["BANK_STATEMENT"],
        "optional_classes_present": [],
    }


def _fec_borderline() -> dict[str, Any]:
    return {
        "c0_mode": "SUBMITTED_DOCUMENT_EVIDENCE_ONLY",
        "c0_state": "PASS",
        "open_web_blocked": True,
        "evidence_contract_id": "fec-borderline",
        "evidence_ids": ["ev-BANK_STATEMENT-001", "ev-TAX_RETURN-002", "ev-CREDIT_REPORT-003"],
        "document_coverage_map": {"BANK_STATEMENT": True, "TAX_RETURN": True, "CREDIT_REPORT": True},
        "extracted_span_map": {},
        "contradiction_flags": [],
        "missing_evidence_flags": [],
        "support_score": 0.47,
        "evidence_sufficiency": "partial",
        "demo_policy_hash": "policy-hash-v1",
        "document_count": 3,
        "required_classes_present": ["BANK_STATEMENT", "TAX_RETURN", "CREDIT_REPORT"],
        "optional_classes_present": [],
    }


# ---------------------------------------------------------------------------
# Test 45 — L3 expands, never executes
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_l3_expands_never_executes() -> None:
    """L3 adapter must return l3_expanded=True and never execute any stage.

    The WorkflowExpansion is a declaration graph — it contains stage contracts
    but no stage outputs (no EvidenceRegister, no ReconciliationResult, etc.).
    Stage execution is exclusively L2's responsibility.
    """
    expansion = _l3.expand({"final_evidence_contract": _fec_pass()})

    assert isinstance(expansion, WorkflowExpansion), (
        "expand() must return a WorkflowExpansion instance."
    )
    assert expansion.l3_expanded is True, (
        "WorkflowExpansion.l3_expanded must be True after expand()."
    )
    assert expansion.route_family == ROUTE_FAMILY, (
        f"route_family must be {ROUTE_FAMILY!r}, got {expansion.route_family!r}."
    )
    assert expansion.stage_count == STAGE_COUNT == 5, (
        f"stage_count must be 5, got {expansion.stage_count}."
    )
    assert len(expansion.stages) == 5, (
        f"stages list must have exactly 5 entries, got {len(expansion.stages)}."
    )

    # No stage should carry an execution output — only contract declarations.
    for stage in expansion.stages:
        assert "evidence_register" not in stage, (
            f"Stage {stage['stage_id']} must not contain evidence_register (L3 does not execute)."
        )
        assert "reconciliation_result" not in stage, (
            f"Stage {stage['stage_id']} must not contain reconciliation_result."
        )
        assert "risk_features" not in stage, (
            f"Stage {stage['stage_id']} must not contain risk_features."
        )
        assert "decision_packet_candidate" not in stage, (
            f"Stage {stage['stage_id']} must not contain decision_packet_candidate."
        )


# ---------------------------------------------------------------------------
# Test 46 — L3 injects evidence_refs only into requires_evidence_refs stages
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_l3_injects_evidence_refs_into_requiring_stages_only() -> None:
    """L3 must inject evidence_refs into stages with requires_evidence_refs=True.

    Stage 1 (requires_evidence_refs=False) must receive an empty
    injected_evidence_refs list. Stages 2-5 must receive the full
    evidence_ids list from the FinalEvidenceContract.
    """
    evidence_ids = ["ev-BANK_STATEMENT-001", "ev-TAX_RETURN-002", "ev-CREDIT_REPORT-003"]
    expansion = _l3.expand({"final_evidence_contract": _fec_pass(evidence_ids)})

    for stage in expansion.stages:
        if stage["requires_evidence_refs"] is False:
            assert stage["injected_evidence_refs"] == [], (
                f"Stage {stage['stage_id']} has requires_evidence_refs=False "
                f"but got non-empty injected_evidence_refs: {stage['injected_evidence_refs']}."
            )
        else:
            assert stage["injected_evidence_refs"] == evidence_ids, (
                f"Stage {stage['stage_id']} has requires_evidence_refs=True "
                f"but injected_evidence_refs={stage['injected_evidence_refs']} "
                f"does not match expected {evidence_ids}."
            )

    assert expansion.evidence_refs == evidence_ids, (
        "WorkflowExpansion.evidence_refs must match FEC evidence_ids."
    )


# ---------------------------------------------------------------------------
# Test 47 — L3 HITL posture: HITL_REQUIRED on missing documents
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_l3_hitl_required_on_missing_documents() -> None:
    """L3 must set hitl_posture=HITL_REQUIRED when required documents are missing.

    Triggers:
      - missing_evidence_flags non-empty → required_document_missing
      - c0_state=FAIL → c0_state_fail_adverse
    Both must appear in hitl_triggers.
    """
    expansion = _l3.expand({"final_evidence_contract": _fec_fail_missing()})

    assert expansion.hitl_posture == HITL_REQUIRED, (
        f"Missing required documents must produce hitl_posture=HITL_REQUIRED, "
        f"got {expansion.hitl_posture!r}."
    )
    assert "required_document_missing" in expansion.hitl_triggers, (
        f"hitl_triggers must contain 'required_document_missing', "
        f"got {expansion.hitl_triggers}."
    )
    assert "c0_state_fail_adverse" in expansion.hitl_triggers, (
        f"hitl_triggers must contain 'c0_state_fail_adverse' for c0_state=FAIL, "
        f"got {expansion.hitl_triggers}."
    )
    assert "DEGRADE_IF_C0_FAIL" in expansion.active_branches, (
        f"active_branches must contain DEGRADE_IF_C0_FAIL when c0_state=FAIL + missing docs, "
        f"got {expansion.active_branches}."
    )


# ---------------------------------------------------------------------------
# Test 48 — L3 HITL posture: HITL_ADVISORY on borderline score band
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_l3_hitl_advisory_on_borderline_score() -> None:
    """L3 must set hitl_posture=HITL_ADVISORY when score in [0.40, 0.55).

    Borderline score band does NOT escalate to HITL_REQUIRED unless a
    stronger trigger (missing docs, contradictions, c0_state_fail) is also
    present. Score 0.47 must yield HITL_ADVISORY.
    """
    expansion = _l3.expand({"final_evidence_contract": _fec_borderline()})

    assert expansion.hitl_posture == HITL_ADVISORY, (
        f"Borderline score 0.47 must produce hitl_posture=HITL_ADVISORY, "
        f"got {expansion.hitl_posture!r}."
    )
    assert "borderline_score_band" in expansion.hitl_triggers, (
        f"hitl_triggers must contain 'borderline_score_band', got {expansion.hitl_triggers}."
    )

    # Verify the raw posture function directly for boundary conditions.
    posture_floor, triggers_floor = _resolve_hitl_posture(
        c0_state="PASS", contradiction_flags=[], missing_evidence_flags=[], support_score=0.40
    )
    assert posture_floor == HITL_ADVISORY, "Score exactly 0.40 must be HITL_ADVISORY."

    posture_ceil, _ = _resolve_hitl_posture(
        c0_state="PASS", contradiction_flags=[], missing_evidence_flags=[], support_score=0.55
    )
    assert posture_ceil == HITL_NONE, "Score exactly 0.55 must be HITL_NONE (above band)."

    posture_below, _ = _resolve_hitl_posture(
        c0_state="PASS", contradiction_flags=[], missing_evidence_flags=[], support_score=0.39
    )
    assert posture_below == HITL_NONE, "Score 0.39 is below band — not borderline, should be HITL_NONE."


# ---------------------------------------------------------------------------
# Test 49 — L3 HITL posture: HITL_NONE on clean PASS FEC
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_l3_hitl_none_on_clean_pass() -> None:
    """L3 must set hitl_posture=HITL_NONE when FEC is PASS with no issues.

    Conditions: c0_state=PASS, no contradictions, no missing docs,
    support_score >= 0.55 (above borderline band).
    """
    expansion = _l3.expand({"final_evidence_contract": _fec_pass()})

    assert expansion.hitl_posture == HITL_NONE, (
        f"Clean PASS FEC (score=0.85, no contradictions, no missing docs) "
        f"must produce hitl_posture=HITL_NONE, got {expansion.hitl_posture!r}."
    )
    assert expansion.hitl_triggers == [], (
        f"HITL_NONE must have empty hitl_triggers, got {expansion.hitl_triggers}."
    )
    assert expansion.active_branches == [], (
        f"Clean PASS must have no active conditional branches, got {expansion.active_branches}."
    )
    assert expansion.c0_state == "PASS"


# ---------------------------------------------------------------------------
# Test 50 — L2 adapters each emit exactly one receipt, no_retrieval + no_l4_write
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_l2_adapters_emit_one_receipt_with_invariants() -> None:
    """Each L2 adapter must emit exactly one L2StepReceipt with:
      - no_retrieval=True (C0 ran first; L2 never calls retrieval)
      - no_l4_write=True (UWG-only write path)
      - receipt_type matching its canonical E-stage constant
    """
    rc = {"final_evidence_contract": _fec_pass(), "request_id": "test-req-001"}
    fec = _fec_pass()
    ev_ids = fec["evidence_ids"]
    span_map = fec["extracted_span_map"]

    # Stage 1
    e1 = EvidenceRegisterAdapter()
    r1 = e1.run(rc)
    assert r1.no_retrieval is True, "E1 must have no_retrieval=True."
    assert r1.no_l4_write is True, "E1 must have no_l4_write=True."
    assert r1.receipt_type == L2_RECEIPT_E1, f"E1 receipt_type wrong: {r1.receipt_type!r}."
    assert r1.success is True, "E1 must succeed with valid FEC."

    er_payload = r1.payload.get("evidence_register", {})

    # Stage 2 — build reconciliation_result dict from e1 output
    recon_input = {
        "evidence_ids": ev_ids,
        "reconciled_spans": {
            ev_id: {
                "evidence_id": ev_id,
                "document_class": span_map[ev_id]["document_class"],
                "field_name": span_map[ev_id]["field_name"],
                "value": span_map[ev_id]["value"],
                "confidence": span_map[ev_id].get("confidence", 0.9),
                "reconciled": True,
            }
            for ev_id, span in span_map.items()
            for _ in [span]
        },
        "missing_required_classes": [],
        "contradiction_flags": [],
    }
    e2 = DocumentReconciliationAdapter()
    r2 = e2.run(er_payload, rc)
    assert r2.no_retrieval is True, "E2 must have no_retrieval=True."
    assert r2.no_l4_write is True, "E2 must have no_l4_write=True."
    assert r2.receipt_type == L2_RECEIPT_E2, f"E2 receipt_type wrong: {r2.receipt_type!r}."

    recon_result = r2.payload.get("reconciliation_result", {})

    # Stage 3
    e3a = FeatureDerivationAdapter()
    r3 = e3a.run(recon_result, rc)
    assert r3.no_retrieval is True, "E3a must have no_retrieval=True."
    assert r3.no_l4_write is True, "E3a must have no_l4_write=True."
    assert r3.receipt_type == L2_RECEIPT_E3, f"E3a receipt_type wrong: {r3.receipt_type!r}."

    risk_features = r3.payload.get("risk_features", {})

    # Stage 4
    e3b = RiskScoringAdapter()
    r4 = e3b.run(risk_features, rc)
    assert r4.no_retrieval is True, "E3b must have no_retrieval=True."
    assert r4.no_l4_write is True, "E3b must have no_l4_write=True."
    assert r4.receipt_type == L2_RECEIPT_E3, f"E3b receipt_type wrong: {r4.receipt_type!r}."

    risk_scores = r4.payload.get("risk_dimension_scores", {})

    # Stage 5
    e5 = DecisionAssemblyAdapter()
    r5 = e5.run(risk_scores, rc)
    assert r5.no_retrieval is True, "E5 must have no_retrieval=True."
    assert r5.no_l4_write is True, "E5 must have no_l4_write=True."
    assert r5.receipt_type == L2_RECEIPT_E5, f"E5 receipt_type wrong: {r5.receipt_type!r}."


# ---------------------------------------------------------------------------
# Test 51 — L2 feature derivation requires evidence_refs from reconciliation
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_l2_feature_derivation_requires_evidence_refs() -> None:
    """FeatureDerivationAdapter must carry evidence_refs from the reconciliation
    result and mark derived_from_evidence=True, open_web_features=False.

    No features may be sourced from open-web retrieval.
    """
    reconciliation_result = {
        "evidence_ids": ["ev-BANK_STATEMENT-001", "ev-TAX_RETURN-002", "ev-CREDIT_REPORT-003"],
        "reconciled_spans": {
            "ev-BANK_STATEMENT-001": {
                "evidence_id": "ev-BANK_STATEMENT-001",
                "document_class": "BANK_STATEMENT",
                "field_name": "average_monthly_balance",
                "value": 8500.0,
                "confidence": 0.9,
                "reconciled": True,
            },
            "ev-TAX_RETURN-002": {
                "evidence_id": "ev-TAX_RETURN-002",
                "document_class": "TAX_RETURN",
                "field_name": "annual_gross_income",
                "value": 95000.0,
                "confidence": 0.9,
                "reconciled": True,
            },
            "ev-CREDIT_REPORT-003": {
                "evidence_id": "ev-CREDIT_REPORT-003",
                "document_class": "CREDIT_REPORT",
                "field_name": "credit_score",
                "value": 740,
                "confidence": 0.95,
                "reconciled": True,
            },
        },
        "missing_required_classes": [],
        "contradiction_flags": [],
        "reconciliation_status": "COMPLETE",
    }
    rc = {"final_evidence_contract": _fec_pass()}

    adapter = FeatureDerivationAdapter()
    receipt = adapter.run(reconciliation_result, rc)

    assert receipt.success is True, (
        f"FeatureDerivationAdapter must succeed with valid reconciliation, got success=False."
    )
    features = receipt.payload.get("risk_features", {})

    assert features.get("derived_from_evidence") is True, (
        "risk_features.derived_from_evidence must be True."
    )
    assert features.get("open_web_features") is False, (
        "risk_features.open_web_features must be False — no open-web retrieval in L2."
    )
    assert set(receipt.evidence_refs) == set(reconciliation_result["evidence_ids"]), (
        f"evidence_refs must match reconciliation evidence_ids, "
        f"got {receipt.evidence_refs}."
    )
    assert features.get("credit_score") == 740, (
        "credit_score must be derived from CREDIT_REPORT span."
    )
    assert features.get("annual_gross_income") == 95000.0, (
        "annual_gross_income must be derived from TAX_RETURN span."
    )


# ---------------------------------------------------------------------------
# Test 52 — L2 decision assembly: verdict + reason_codes locked (immutable intent)
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_l2_decision_assembly_verdict_and_reason_codes_locked() -> None:
    """DecisionAssemblyAdapter must produce a sealed artifact with:
      - verdict in {APPROVE, REFER, DECLINE}
      - reason_codes non-empty list
      - artifact_sealed=True
      - verdict_locked=True
      - reason_codes_locked=True
      - rationale_source="PENDING_PA_COMPILER" (PA compiler runs in W4)
    The verdict and reason_codes must be immutable once sealed — the PA compiler
    only adds rationale prose; it cannot change verdict or reason_codes.
    """
    # Build a risk_dimension_scores dict for a strong APPROVE case.
    risk_scores = {
        "dim_scores": {
            "creditworthiness": 0.8,
            "income_stability": 1.0,
            "debt_service_capacity": 0.75,
            "document_completeness": 0.85,
            "contradiction_risk": 1.0,
        },
        "dim_evidence": {},
        "aggregate_score": 0.88,
        "scored_dimensions": [
            "creditworthiness", "income_stability", "debt_service_capacity",
            "document_completeness", "contradiction_risk",
        ],
        "evidence_ids": ["ev-BANK_STATEMENT-001", "ev-TAX_RETURN-002", "ev-CREDIT_REPORT-003"],
    }
    rc = {"final_evidence_contract": _fec_pass()}

    adapter = DecisionAssemblyAdapter()
    receipt = adapter.run(risk_scores, rc)

    assert receipt.success is True, "DecisionAssemblyAdapter must succeed."
    assert receipt.receipt_type == L2_RECEIPT_E5

    candidate = receipt.payload.get("decision_packet_candidate", {})

    assert candidate.get("verdict") in ("APPROVE", "REFER", "DECLINE"), (
        f"verdict must be APPROVE/REFER/DECLINE, got {candidate.get('verdict')!r}."
    )
    assert candidate.get("verdict") == "APPROVE", (
        f"aggregate_score=0.88 >= 0.70 threshold must produce APPROVE, "
        f"got {candidate.get('verdict')!r}."
    )
    assert isinstance(candidate.get("reason_codes"), list) and len(candidate["reason_codes"]) > 0, (
        "reason_codes must be a non-empty list."
    )
    assert candidate.get("artifact_sealed") is True, "artifact_sealed must be True."
    assert candidate.get("verdict_locked") is True, "verdict_locked must be True."
    assert candidate.get("reason_codes_locked") is True, "reason_codes_locked must be True."
    assert candidate.get("rationale_source") == "PENDING_PA_COMPILER", (
        f"rationale_source must be PENDING_PA_COMPILER, got {candidate.get('rationale_source')!r}. "
        "PA compiler (LLM firewall) runs in W4 — verdict must not wait for LLM."
    )
    assert candidate.get("rationale") == "", (
        "rationale must be empty at L2 assembly time — populated by PA compiler in W4."
    )
    assert set(candidate.get("evidence_refs", [])) == set(risk_scores["evidence_ids"]), (
        "evidence_refs in sealed packet must match evidence_ids from risk scores."
    )

    # Verify DECLINE case.
    low_scores = dict(risk_scores, dim_scores={"creditworthiness": 0.1, "income_stability": 0.1}, aggregate_score=0.10)
    r_decline = adapter.run(low_scores, rc)
    cand_decline = r_decline.payload.get("decision_packet_candidate", {})
    assert cand_decline.get("verdict") == "DECLINE", (
        f"aggregate_score=0.10 must produce DECLINE, got {cand_decline.get('verdict')!r}."
    )
