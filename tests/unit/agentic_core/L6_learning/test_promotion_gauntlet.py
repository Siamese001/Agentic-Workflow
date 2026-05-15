"""W1 tests for PromotionGauntlet — G29 gate ID, proof fields, and fail-closed validation.

Covers:
- GATE_ID identity semantics (not a GateVerdict substitute)
- gate_id populated in L6GauntletResult
- Missing proof field failure codes (Checks 7-10)
- Negative: GATE_ID alone does NOT satisfy promotion; gate_id in result does not imply passed
"""
from __future__ import annotations

import pytest

from agentic_core.L6_learning import (
    FutureRunPromotionRequest,
    L6GauntletResult,
    ProposalPacket,
    ProposalType,
    ProofType,
)
from agentic_core.L6_learning.promotion_gauntlet import PromotionGauntlet


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minimal_request(**overrides) -> FutureRunPromotionRequest:
    """Build a minimal FutureRunPromotionRequest with all required proof fields set.

    Override specific fields via kwargs to exercise failure conditions.
    """
    defaults = dict(
        request_id="req-test-001",
        run_id="run-test-001",
        proposal_packets=(),
        rollback_plan_ref="rollback://test-001",
        audit_manifest_ref="manifest://test-001",
        completed_eval_record_ref="eval://test-001",
        rca_packet_ref="rca://test-001",
        calibration_proof_ref="calib://test-001",
    )
    defaults.update(overrides)
    return FutureRunPromotionRequest(**defaults)


def _make_proposal(proposal_type: ProposalType) -> ProposalPacket:
    return ProposalPacket(
        proposal_id="prop-001",
        run_id="run-test-001",
        proposal_type=proposal_type,
    )


gauntlet = PromotionGauntlet()


# ---------------------------------------------------------------------------
# GATE_ID identity tests
# ---------------------------------------------------------------------------

def test_gate_id_constant_is_g29():
    """GATE_ID class constant must equal 'G29'."""
    assert PromotionGauntlet.GATE_ID == "G29"


def test_gate_id_is_string_not_verdict():
    """GATE_ID must be a plain string, not a GateVerdict or proof object."""
    assert isinstance(PromotionGauntlet.GATE_ID, str)


def test_gate_id_populated_in_result():
    """gate_id field on L6GauntletResult must be populated from GATE_ID."""
    req = _minimal_request()
    result = gauntlet.run_gauntlet(req)
    assert result.gate_id == PromotionGauntlet.GATE_ID == "G29"


def test_gate_id_is_not_a_gate_verdict():
    """Critical: GATE_ID alone must NOT produce a passing result.

    A request with all proof refs empty must fail even though GATE_ID='G29'
    is present on the gauntlet. The string identifier does not substitute
    for 00C GateVerdict evidence.
    """
    req = _minimal_request(
        audit_manifest_ref="",
        completed_eval_record_ref="",
        rca_packet_ref="",
        calibration_proof_ref="",
    )
    result = gauntlet.run_gauntlet(req)
    # gate_id is populated — it is the identifier
    assert result.gate_id == "G29"
    # but the result must NOT pass — GATE_ID is not proof
    assert result.passed is False
    assert len(result.failures) > 0


def test_gate_id_not_in_failures_as_substitute():
    """gate_id value must not appear in failures list as if it were evidence."""
    req = _minimal_request(audit_manifest_ref="", completed_eval_record_ref="")
    result = gauntlet.run_gauntlet(req)
    # 'G29' should not be used as a failure-resolution value
    for failure in result.failures:
        assert "G29" not in failure or "GATE_ID" not in failure, (
            f"Unexpected G29 in failure message: {failure}"
        )


def test_gate_id_field_exists_on_result_dataclass():
    """L6GauntletResult must have gate_id field with default ''."""
    fields = list(L6GauntletResult.__dataclass_fields__)
    assert "gate_id" in fields


# ---------------------------------------------------------------------------
# Check 7: audit_manifest_ref required for every promotion
# ---------------------------------------------------------------------------

def test_missing_audit_manifest_ref_fails_gauntlet():
    """Empty audit_manifest_ref must produce AUDIT_MANIFEST_REQUIRED failure."""
    req = _minimal_request(audit_manifest_ref="")
    result = gauntlet.run_gauntlet(req)
    assert result.passed is False
    assert any("AUDIT_MANIFEST_REQUIRED" in f for f in result.failures), (
        f"Expected AUDIT_MANIFEST_REQUIRED in failures: {result.failures}"
    )


def test_present_audit_manifest_ref_passes_check7():
    """Non-empty audit_manifest_ref must not trigger Check 7 failure."""
    req = _minimal_request(audit_manifest_ref="manifest://test")
    result = gauntlet.run_gauntlet(req)
    assert not any("AUDIT_MANIFEST_REQUIRED" in f for f in result.failures)


# ---------------------------------------------------------------------------
# Check 8: completed_eval_record_ref required for every promotion
# ---------------------------------------------------------------------------

def test_missing_completed_eval_record_ref_fails_gauntlet():
    """Empty completed_eval_record_ref must produce COMPLETED_EVAL_RECORD_REQUIRED failure."""
    req = _minimal_request(completed_eval_record_ref="")
    result = gauntlet.run_gauntlet(req)
    assert result.passed is False
    assert any("COMPLETED_EVAL_RECORD_REQUIRED" in f for f in result.failures), (
        f"Expected COMPLETED_EVAL_RECORD_REQUIRED in failures: {result.failures}"
    )


def test_present_completed_eval_record_ref_passes_check8():
    """Non-empty completed_eval_record_ref must not trigger Check 8 failure."""
    req = _minimal_request(completed_eval_record_ref="eval://test")
    result = gauntlet.run_gauntlet(req)
    assert not any("COMPLETED_EVAL_RECORD_REQUIRED" in f for f in result.failures)


# ---------------------------------------------------------------------------
# Check 9: rca_packet_ref required for corrective/policy/prompt/rubric/judge/cache types
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("proposal_type", [
    ProposalType.PROMPT_IMPROVEMENT,
    ProposalType.RUBRIC_IMPROVEMENT,
    ProposalType.JUDGE_CALIBRATION,
    ProposalType.CACHE_THRESHOLD,
    ProposalType.SOURCE_RELIABILITY,
    ProposalType.RETRIEVAL_PROFILE,
    ProposalType.CHUNKING_PROFILE,
])
def test_missing_rca_packet_ref_fails_for_rca_required_types(proposal_type):
    """Empty rca_packet_ref must produce RCA_PACKET_REQUIRED failure for applicable types."""
    req = _minimal_request(
        proposal_packets=(_make_proposal(proposal_type),),
        rca_packet_ref="",
        # Keep calibration set to avoid noise for JUDGE_CALIBRATION
        calibration_proof_ref="calib://test",
    )
    result = gauntlet.run_gauntlet(req)
    assert any("RCA_PACKET_REQUIRED" in f for f in result.failures), (
        f"Expected RCA_PACKET_REQUIRED for {proposal_type.name}: {result.failures}"
    )


def test_missing_rca_packet_ref_for_prompt_improvement_fails():
    """Named test: PROMPT_IMPROVEMENT + empty rca_packet_ref → Check 9 failure."""
    req = _minimal_request(
        proposal_packets=(_make_proposal(ProposalType.PROMPT_IMPROVEMENT),),
        rca_packet_ref="",
    )
    result = gauntlet.run_gauntlet(req)
    assert any("RCA_PACKET_REQUIRED" in f for f in result.failures)


def test_missing_rca_packet_ref_for_rubric_improvement_fails():
    """Named test: RUBRIC_IMPROVEMENT + empty rca_packet_ref → Check 9 failure."""
    req = _minimal_request(
        proposal_packets=(_make_proposal(ProposalType.RUBRIC_IMPROVEMENT),),
        rca_packet_ref="",
    )
    result = gauntlet.run_gauntlet(req)
    assert any("RCA_PACKET_REQUIRED" in f for f in result.failures)


def test_missing_rca_packet_ref_for_cache_threshold_fails():
    """Named test: CACHE_THRESHOLD + empty rca_packet_ref → Check 9 failure."""
    req = _minimal_request(
        proposal_packets=(_make_proposal(ProposalType.CACHE_THRESHOLD),),
        rca_packet_ref="",
    )
    result = gauntlet.run_gauntlet(req)
    assert any("RCA_PACKET_REQUIRED" in f for f in result.failures)


def test_rca_packet_ref_not_required_for_entity_alias():
    """ENTITY_ALIAS is not in RCA-required types — missing rca_packet_ref must not fail Check 9."""
    req = _minimal_request(
        proposal_packets=(_make_proposal(ProposalType.ENTITY_ALIAS),),
        rca_packet_ref="",
    )
    result = gauntlet.run_gauntlet(req)
    assert not any("RCA_PACKET_REQUIRED" in f for f in result.failures)


# ---------------------------------------------------------------------------
# Check 10: calibration_proof_ref required for JUDGE_CALIBRATION
# ---------------------------------------------------------------------------

def test_missing_calibration_proof_for_judge_calibration_fails():
    """Empty calibration_proof_ref with JUDGE_CALIBRATION proposal → Check 10 failure."""
    req = _minimal_request(
        proposal_packets=(_make_proposal(ProposalType.JUDGE_CALIBRATION),),
        calibration_proof_ref="",
    )
    result = gauntlet.run_gauntlet(req)
    assert result.passed is False
    assert any("CALIBRATION_PROOF_REQUIRED" in f for f in result.failures), (
        f"Expected CALIBRATION_PROOF_REQUIRED in failures: {result.failures}"
    )


def test_calibration_proof_not_required_for_prompt_improvement():
    """PROMPT_IMPROVEMENT does not require calibration_proof_ref (Check 10 must not fire)."""
    req = _minimal_request(
        proposal_packets=(_make_proposal(ProposalType.PROMPT_IMPROVEMENT),),
        calibration_proof_ref="",
    )
    result = gauntlet.run_gauntlet(req)
    # Check 9 may fire (missing rca_packet_ref omitted here intentionally)
    # but Check 10 must NOT fire for PROMPT_IMPROVEMENT
    assert not any("CALIBRATION_PROOF_REQUIRED" in f for f in result.failures)


# ---------------------------------------------------------------------------
# Passing path: all required refs present
# ---------------------------------------------------------------------------

def test_fully_populated_request_passes_gauntlet():
    """A request with all required proof refs set must pass the gauntlet."""
    req = _minimal_request(
        proposal_packets=(_make_proposal(ProposalType.ENTITY_ALIAS),),
    )
    result = gauntlet.run_gauntlet(req)
    assert result.passed is True
    assert result.failures == []
    assert result.gate_id == "G29"


def test_proof_fields_exist_on_future_run_promotion_request():
    """FutureRunPromotionRequest must expose all four W1 proof ref fields."""
    fields = list(FutureRunPromotionRequest.__dataclass_fields__)
    assert "audit_manifest_ref" in fields
    assert "completed_eval_record_ref" in fields
    assert "rca_packet_ref" in fields
    assert "calibration_proof_ref" in fields  # pre-existing, must not be duplicated
    # Confirm no duplicates in field list
    assert len(fields) == len(set(fields)), "Duplicate fields detected in FutureRunPromotionRequest"
