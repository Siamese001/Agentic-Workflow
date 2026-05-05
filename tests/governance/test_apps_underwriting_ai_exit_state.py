"""W5.4 Governance tests — Exit/State invariants (apps_underwriting_ai).

10 tests covering:
  59 — produce_fec() emits route_family, reason_code_bundle, evidence_coverage,
       public_trust_receipt with all required fields
  60 — produce_fec() evidence_coverage counts match FEC fields
  61 — produce_fec() public_trust_receipt.demo_mode is always True
  62 — Exit emits exactly one X3 per run; second call raises RuntimeError
  63 — Exit fail-closed: missing FEC → X3E_SAFE_ABSTAIN
  64 — Exit fail-closed: missing demo_policy_hash → X3E_SAFE_ABSTAIN
  65 — Exit APPROVE verdict + clean FEC → X3A_APPROVE
  66 — Exit HITL_REQUIRED posture escalates APPROVE → X3B_REFER
  67 — Exit UNKNOWN verdict → X3E_SAFE_ABSTAIN (fail-closed unknown)
  68 — W5.3 proof: l4_write_attempted=False and l6_post_run_only=True on every
       exit bundle (UWG-only write path; L6 after-runtime only)

Plan: apps-underwriting-ai-spine-hardening-d7f3b2 W5.3 + W5.4.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_underwriting_ai.cert.fec_producer import PublicTrustReceipt, produce_fec
from apps_underwriting_ai.integrations.underwriting_exit_fec_producer import (
    X3A_APPROVE,
    X3B_REFER,
    X3C_DECLINE,
    X3D_INSUFFICIENT,
    X3E_SAFE_ABSTAIN,
    _VALID_X3,
    _select_x3_disposition,
    UnderwritingExitFecProducer,
    validate_exit_preconditions,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_PASS_FEC: dict[str, Any] = {
    "c0_mode": "SUBMITTED_DOCUMENT_EVIDENCE_ONLY",
    "c0_state": "PASS",
    "open_web_blocked": True,
    "evidence_contract_id": "fec-exit-test-001",
    "evidence_ids": ["ev-BANK_STATEMENT-001", "ev-TAX_RETURN-002", "ev-CREDIT_REPORT-003"],
    "document_coverage_map": {"BANK_STATEMENT": True, "TAX_RETURN": True, "CREDIT_REPORT": True},
    "extracted_span_map": {},
    "contradiction_flags": [],
    "missing_evidence_flags": [],
    "support_score": 0.88,
    "evidence_sufficiency": "sufficient",
    "demo_policy_hash": "policy-hash-v1",
    "document_count": 3,
    "required_classes_present": ["BANK_STATEMENT", "TAX_RETURN", "CREDIT_REPORT"],
    "optional_classes_present": [],
}

_CLEAN_CONTEXT: dict[str, Any] = {
    "final_evidence_contract": _PASS_FEC,
    "demo_policy_hash": "policy-hash-v1",
    "blueprint_hash": "blueprint-hash-v1",
    "route_contract": {"route_id": "R3R4_MANAGED_WORKFLOW"},
    "verdict": "APPROVE",
    "reason_code_bundle": ["RC000_CREDIT_SCORE_STRONG", "RC001_INCOME_VERIFIED"],
    "hitl_posture": "HITL_NONE",
    "route_family": "R3R4_MANAGED_WORKFLOW",
    "deterministic_rationale_fallback_used": True,
    "firewall_passed": False,
    "exit_disposition": "X3A_APPROVE",
    "demo_packet_id": "pkt-test-001",
    "replay_key": "replay-abc123xyz",
}


# ---------------------------------------------------------------------------
# Test 59 — produce_fec() emits all W5.1 new fields
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_produce_fec_emits_w5_fields() -> None:
    """produce_fec() must emit route_family, reason_code_bundle, evidence_coverage,
    hitl_posture, deterministic_rationale_fallback_used, and public_trust_receipt.
    """
    ctx = dict(_CLEAN_CONTEXT)
    result = produce_fec(ctx)

    assert result["schema_version"] == "1.1", (
        f"schema_version must be '1.1' after W5.1, got {result['schema_version']!r}."
    )
    assert result["route_family"] == "R3R4_MANAGED_WORKFLOW", (
        f"route_family must be 'R3R4_MANAGED_WORKFLOW', got {result['route_family']!r}."
    )
    assert isinstance(result["reason_code_bundle"], list), (
        "reason_code_bundle must be a list."
    )
    assert result["reason_code_bundle"] == ["RC000_CREDIT_SCORE_STRONG", "RC001_INCOME_VERIFIED"]

    assert "evidence_coverage" in result, "evidence_coverage must be present in FEC output."
    cov = result["evidence_coverage"]
    for key in (
        "required_classes_present", "optional_classes_present",
        "missing_required_classes", "contradiction_flags_count",
        "documents_received_count", "documents_missing_count",
    ):
        assert key in cov, f"evidence_coverage missing key: {key!r}."

    assert "hitl_posture" in result, "hitl_posture must be present."
    assert "deterministic_rationale_fallback_used" in result

    ptr = result["public_trust_receipt"]
    assert isinstance(ptr, dict), "public_trust_receipt must be a dict."
    for field_name in PublicTrustReceipt.__dataclass_fields__:
        assert field_name in ptr, (
            f"public_trust_receipt missing field: {field_name!r}."
        )


# ---------------------------------------------------------------------------
# Test 60 — produce_fec() evidence_coverage counts match FEC
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_produce_fec_evidence_coverage_counts_match_fec() -> None:
    """evidence_coverage counts must be derived from FinalEvidenceContract fields."""
    ctx = dict(_CLEAN_CONTEXT)
    result = produce_fec(ctx)
    cov = result["evidence_coverage"]

    assert cov["documents_received_count"] == 3, (
        f"documents_received_count must be 3 (from document_count), got {cov['documents_received_count']}."
    )
    assert cov["documents_missing_count"] == 0, (
        f"documents_missing_count must be 0 (empty missing_evidence_flags), got {cov['documents_missing_count']}."
    )
    assert cov["contradiction_flags_count"] == 0, (
        f"contradiction_flags_count must be 0, got {cov['contradiction_flags_count']}."
    )
    assert set(cov["required_classes_present"]) == {"BANK_STATEMENT", "TAX_RETURN", "CREDIT_REPORT"}, (
        f"required_classes_present mismatch: {cov['required_classes_present']}."
    )
    assert cov["missing_required_classes"] == [], (
        f"missing_required_classes must be empty for PASS FEC, got {cov['missing_required_classes']}."
    )

    # Test with missing documents.
    missing_fec = dict(_PASS_FEC, missing_evidence_flags=["TAX_RETURN"], document_count=2)
    ctx2 = dict(_CLEAN_CONTEXT, final_evidence_contract=missing_fec)
    result2 = produce_fec(ctx2)
    cov2 = result2["evidence_coverage"]
    assert cov2["documents_missing_count"] == 1, (
        f"documents_missing_count must be 1 when one class is missing, got {cov2['documents_missing_count']}."
    )
    assert "TAX_RETURN" in cov2["missing_required_classes"]


# ---------------------------------------------------------------------------
# Test 61 — produce_fec() public_trust_receipt.demo_mode is always True
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_produce_fec_public_trust_receipt_demo_mode_always_true() -> None:
    """PublicTrustReceipt.demo_mode must always be True.

    This app produces synthetic demo packets only — never real applicant data.
    """
    result = produce_fec(_CLEAN_CONTEXT)
    ptr = result["public_trust_receipt"]
    assert ptr["demo_mode"] is True, (
        "public_trust_receipt.demo_mode must always be True — synthetic demo only."
    )

    # Even with empty context, demo_mode must be True.
    result_empty = produce_fec({})
    assert result_empty["public_trust_receipt"]["demo_mode"] is True, (
        "demo_mode must be True even with empty run_context."
    )

    # Verify replay_key_prefix is correctly set (first 12 chars).
    assert result["public_trust_receipt"]["replay_key_prefix"] == "replay-abc12", (
        f"replay_key_prefix must be first 12 chars of replay_key, "
        f"got {result['public_trust_receipt']['replay_key_prefix']!r}."
    )


# ---------------------------------------------------------------------------
# Test 62 — Exit emits exactly one X3 per run; second call raises RuntimeError
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_exit_emits_exactly_one_x3_second_call_raises() -> None:
    """UnderwritingExitFecProducer must enforce exactly-one-X3 per instance.

    The second call to produce_exit_bundle() on the same instance must raise
    RuntimeError. Callers must instantiate a fresh producer per run.
    """
    producer = UnderwritingExitFecProducer()
    bundle = producer.produce_exit_bundle(_PASS_FEC, _CLEAN_CONTEXT)

    assert bundle["x3_emitted"] is True, "x3_emitted must be True after first call."
    assert producer.x3_emitted is True, "producer.x3_emitted must be True after first call."
    assert bundle["x3_disposition"] in _VALID_X3, (
        f"x3_disposition must be a valid X3 class, got {bundle['x3_disposition']!r}."
    )

    with pytest.raises(RuntimeError, match="Exactly one X3"):
        producer.produce_exit_bundle(_PASS_FEC, _CLEAN_CONTEXT)


# ---------------------------------------------------------------------------
# Test 63 — Exit fail-closed: missing FEC → X3E_SAFE_ABSTAIN
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_exit_fail_closed_missing_fec() -> None:
    """Missing FinalEvidenceContract must produce X3E_SAFE_ABSTAIN.

    The exit must fail closed — a None or empty FEC is never passable.
    """
    producer = UnderwritingExitFecProducer()
    bundle = producer.produce_exit_bundle(None, _CLEAN_CONTEXT)

    assert bundle["x3_disposition"] == X3E_SAFE_ABSTAIN, (
        f"Missing FEC must produce X3E_SAFE_ABSTAIN, got {bundle['x3_disposition']!r}."
    )
    assert bundle["x3_emitted"] is True
    assert len(bundle["violations"]) > 0, "violations must be non-empty when FEC is missing."
    assert any("final_evidence_contract" in v for v in bundle["violations"]), (
        "violations must name the missing final_evidence_contract."
    )

    # validate_exit_preconditions directly.
    ok, viols = validate_exit_preconditions(None, _CLEAN_CONTEXT)
    assert ok is False
    assert any("final_evidence_contract" in v for v in viols)


# ---------------------------------------------------------------------------
# Test 64 — Exit fail-closed: missing demo_policy_hash → X3E_SAFE_ABSTAIN
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_exit_fail_closed_missing_policy_hash() -> None:
    """Missing demo_policy_hash in run_context must produce X3E_SAFE_ABSTAIN."""
    ctx_no_policy = {k: v for k, v in _CLEAN_CONTEXT.items() if k != "demo_policy_hash"}
    producer = UnderwritingExitFecProducer()
    bundle = producer.produce_exit_bundle(_PASS_FEC, ctx_no_policy)

    assert bundle["x3_disposition"] == X3E_SAFE_ABSTAIN, (
        f"Missing demo_policy_hash must produce X3E_SAFE_ABSTAIN, "
        f"got {bundle['x3_disposition']!r}."
    )
    assert any("demo_policy_hash" in v for v in bundle["violations"]), (
        "violations must name the missing demo_policy_hash."
    )

    # Also test missing blueprint_hash.
    ctx_no_bp = {k: v for k, v in _CLEAN_CONTEXT.items() if k != "blueprint_hash"}
    producer2 = UnderwritingExitFecProducer()
    bundle2 = producer2.produce_exit_bundle(_PASS_FEC, ctx_no_bp)
    assert bundle2["x3_disposition"] == X3E_SAFE_ABSTAIN
    assert any("blueprint_hash" in v for v in bundle2["violations"])


# ---------------------------------------------------------------------------
# Test 65 — Exit APPROVE verdict + clean FEC → X3A_APPROVE
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_exit_approve_verdict_clean_fec_yields_x3a() -> None:
    """Clean APPROVE with PASS FEC, reason_codes, HITL_NONE → X3A_APPROVE."""
    producer = UnderwritingExitFecProducer()
    bundle = producer.produce_exit_bundle(_PASS_FEC, _CLEAN_CONTEXT)

    assert bundle["x3_disposition"] == X3A_APPROVE, (
        f"APPROVE + PASS FEC + HITL_NONE must yield X3A_APPROVE, "
        f"got {bundle['x3_disposition']!r}."
    )
    assert bundle["violations"] == [], "No violations expected for clean APPROVE."
    assert bundle["verdict"] == "APPROVE"
    assert bundle["c0_state"] == "PASS"

    # Verify the disposition selector directly for all verdict/posture combos.
    assert _select_x3_disposition("APPROVE", "HITL_NONE", "PASS", [], ["RC000"]) == X3A_APPROVE
    assert _select_x3_disposition("REFER", "HITL_NONE", "PASS", [], ["RC000"]) == X3B_REFER
    assert _select_x3_disposition("DECLINE", "HITL_NONE", "PASS", [], ["RC000"]) == X3C_DECLINE
    assert _select_x3_disposition("INSUFFICIENT_EVIDENCE", "HITL_NONE", "PASS", [], []) == X3D_INSUFFICIENT
    assert _select_x3_disposition("APPROVE", "HITL_NONE", "FAIL", [], ["RC000"]) == X3E_SAFE_ABSTAIN


# ---------------------------------------------------------------------------
# Test 66 — Exit HITL_REQUIRED escalates APPROVE → X3B_REFER
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_exit_hitl_required_escalates_approve_to_x3b() -> None:
    """HITL_REQUIRED posture must escalate any non-insufficient verdict to X3B_REFER.

    Even a clean APPROVE verdict is escalated to REFER for human review when
    the L3 workflow adapter resolved HITL_REQUIRED.
    """
    ctx_hitl = dict(_CLEAN_CONTEXT, hitl_posture="HITL_REQUIRED")
    producer = UnderwritingExitFecProducer()
    bundle = producer.produce_exit_bundle(_PASS_FEC, ctx_hitl)

    assert bundle["x3_disposition"] == X3B_REFER, (
        f"HITL_REQUIRED must escalate APPROVE to X3B_REFER, "
        f"got {bundle['x3_disposition']!r}."
    )
    assert bundle["hitl_posture"] == "HITL_REQUIRED"
    assert bundle["violations"] == []

    # HITL_ADVISORY also escalates.
    ctx_advisory = dict(_CLEAN_CONTEXT, hitl_posture="HITL_ADVISORY")
    producer2 = UnderwritingExitFecProducer()
    bundle2 = producer2.produce_exit_bundle(_PASS_FEC, ctx_advisory)
    assert bundle2["x3_disposition"] == X3B_REFER, (
        f"HITL_ADVISORY must also escalate to X3B_REFER, got {bundle2['x3_disposition']!r}."
    )


# ---------------------------------------------------------------------------
# Test 67 — Exit UNKNOWN verdict → X3E_SAFE_ABSTAIN
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_exit_unknown_verdict_yields_x3e() -> None:
    """An unknown or empty verdict must produce X3E_SAFE_ABSTAIN.

    The exit must never pass with a verdict it cannot classify — fail closed.
    """
    for bad_verdict in ("UNKNOWN", "MAYBE", "ERROR"):
        ctx_bad = dict(_CLEAN_CONTEXT, verdict=bad_verdict)
        producer = UnderwritingExitFecProducer()
        bundle = producer.produce_exit_bundle(_PASS_FEC, ctx_bad)
        assert bundle["x3_disposition"] == X3E_SAFE_ABSTAIN, (
            f"verdict={bad_verdict!r} must yield X3E_SAFE_ABSTAIN, "
            f"got {bundle['x3_disposition']!r}."
        )

    # Via the selector directly — empty string also falls through to unknown catch → X3E.
    assert _select_x3_disposition("MAYBE", "HITL_NONE", "PASS", [], ["RC000"]) == X3E_SAFE_ABSTAIN
    assert _select_x3_disposition("", "HITL_NONE", "PASS", [], ["RC000"]) == X3E_SAFE_ABSTAIN


# ---------------------------------------------------------------------------
# Test 68 — W5.3 proof: l4_write_attempted=False, l6_post_run_only=True
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_exit_bundle_uwg_only_and_l6_post_run_invariants() -> None:
    """W5.3 proof: every exit bundle must assert UWG-only write path and
    L6 post-run-only discipline, regardless of X3 disposition class.

    Verified across all five X3 paths:
      X3A — clean APPROVE
      X3B — HITL_REQUIRED escalation
      X3C — DECLINE verdict
      X3D — INSUFFICIENT_EVIDENCE
      X3E — precondition violation (fail-closed)
    """
    scenarios: list[tuple[str, dict[str, Any] | None, dict[str, Any]]] = [
        # (label, fec, ctx)
        (
            "X3A_APPROVE",
            _PASS_FEC,
            _CLEAN_CONTEXT,
        ),
        (
            "X3B_REFER_HITL",
            _PASS_FEC,
            dict(_CLEAN_CONTEXT, hitl_posture="HITL_REQUIRED"),
        ),
        (
            "X3C_DECLINE",
            _PASS_FEC,
            dict(_CLEAN_CONTEXT, verdict="DECLINE"),
        ),
        (
            "X3D_INSUFFICIENT",
            _PASS_FEC,
            dict(_CLEAN_CONTEXT, verdict="INSUFFICIENT_EVIDENCE", reason_code_bundle=[]),
        ),
        (
            "X3E_SAFE_ABSTAIN_missing_fec",
            None,
            _CLEAN_CONTEXT,
        ),
    ]

    for label, fec, ctx in scenarios:
        producer = UnderwritingExitFecProducer()
        bundle = producer.produce_exit_bundle(fec, ctx)

        assert bundle.get("l4_write_attempted") is False, (
            f"[{label}] l4_write_attempted must be False — UWG is the only write path."
        )
        assert bundle.get("l6_post_run_only") is True, (
            f"[{label}] l6_post_run_only must be True — L6 observability is after-runtime only."
        )
        assert bundle.get("durable_write_path") == "UWG_ONLY", (
            f"[{label}] durable_write_path must be 'UWG_ONLY', got {bundle.get('durable_write_path')!r}."
        )
        assert bundle.get("demo_mode") is True, (
            f"[{label}] demo_mode must be True — synthetic demo only."
        )
        assert bundle.get("x3_disposition") in _VALID_X3, (
            f"[{label}] x3_disposition {bundle.get('x3_disposition')!r} not in valid X3 set."
        )
        assert bundle.get("x3_emitted") is True, (
            f"[{label}] x3_emitted must be True after produce_exit_bundle()."
        )
