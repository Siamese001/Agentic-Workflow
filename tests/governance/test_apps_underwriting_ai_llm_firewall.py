"""W4.2 Governance tests — LLM Rationale Firewall (apps_underwriting_ai).

6 tests covering:
  53 — PA compiler runs BEFORE any LLM call (firewall_passed=True on clean input)
  54 — PromptAssemblyError forces deterministic fallback (pa_error=True)
  55 — Verdict immutability: firewall blocks when verdict changes post-compile
  56 — Reason-codes immutability: firewall blocks when reason_codes change post-compile
  57 — LLM callable exception → deterministic fallback, firewall_passed=False
  58 — Accepted LLM rationale is returned as-is; verdict + reason_codes unchanged

Plan: apps-underwriting-ai-spine-hardening-d7f3b2 W4.2.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_underwriting_ai.integrations.underwriting_llm_firewall import (  # noqa: E402
    FIREWALL_MODE_STRICT,
    FirewallResult,
    UnderwritingLLMFirewall,
    _check_immutability,
    _hash,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_VERDICT = "APPROVE"
_REASON_CODES = ["RC000_CREDIT_SCORE_STRONG", "RC001_INCOME_VERIFIED"]
_DET_RATIONALE = "Application meets all underwriting criteria."

_C0_BUNDLE: dict[str, Any] = {
    "c0_mode": "SUBMITTED_DOCUMENT_EVIDENCE_ONLY",
    "c0_state": "PASS",
    "open_web_blocked": True,
    "evidence_contract_id": "fec-fw-test-001",
    "evidence_ids": ["ev-BANK_STATEMENT-001", "ev-TAX_RETURN-002", "ev-CREDIT_REPORT-003"],
    "contradiction_flags": [],
    "missing_evidence_flags": [],
    "support_score": 0.88,
    "evidence_sufficiency": "sufficient",
}

_firewall = UnderwritingLLMFirewall(mode=FIREWALL_MODE_STRICT)


# ---------------------------------------------------------------------------
# Test 53 — PA compiler runs BEFORE any LLM call
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_pa_compiler_runs_before_llm_call() -> None:
    """PA compiler must run before any LLM call.

    When a valid verdict, reason_codes, and c0_bundle are supplied,
    firewall.gate() must:
      - succeed (firewall_passed=True)
      - bind verdict_hash and reason_codes_hash into the artifact
      - return a non-empty artifact_id and artifact_hash
    No LLM callable is supplied — the firewall must still compile successfully.
    """
    result = _firewall.gate(
        verdict=_VERDICT,
        reason_codes=_REASON_CODES,
        c0_bundle=_C0_BUNDLE,
        deterministic_rationale=_DET_RATIONALE,
        request_id="req-fw-001",
        run_id="run-001",
        trace_id="trace-001",
    )

    assert isinstance(result, FirewallResult), (
        "firewall.gate() must return a FirewallResult instance."
    )
    assert result.firewall_passed is True, (
        f"PA compilation must succeed with valid inputs, got firewall_passed=False. "
        f"failure_reason={result.failure_reason!r}."
    )
    assert result.pa_error is False, (
        f"No PA error expected on valid inputs, got pa_error=True."
    )
    assert result.artifact_id != "", "artifact_id must be non-empty after successful compilation."
    assert result.artifact_hash != "", "artifact_hash must be non-empty after successful compilation."

    # Verify hash bindings are correct.
    expected_verdict_hash = _hash(_VERDICT)
    expected_rc_hash = _hash(sorted(_REASON_CODES))
    assert result.verdict_hash == expected_verdict_hash, (
        f"verdict_hash mismatch: expected {expected_verdict_hash[:12]}…, "
        f"got {result.verdict_hash[:12]}…"
    )
    assert result.reason_codes_hash == expected_rc_hash, (
        f"reason_codes_hash mismatch: expected {expected_rc_hash[:12]}…, "
        f"got {result.reason_codes_hash[:12]}…"
    )

    # With no LLM callable the rationale falls through to deterministic.
    assert result.rationale == _DET_RATIONALE, (
        "Without an llm_callable the deterministic rationale must be returned."
    )
    assert result.deterministic_fallback_used is True, (
        "deterministic_fallback_used must be True when no llm_callable is supplied."
    )
    assert result.failure_reason == "no_llm_callable", (
        f"failure_reason must be 'no_llm_callable', got {result.failure_reason!r}."
    )


# ---------------------------------------------------------------------------
# Test 54 — PromptAssemblyError forces deterministic fallback
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_pa_assembly_error_forces_deterministic_fallback() -> None:
    """When compile_artifact() raises PromptAssemblyError, the firewall must:
      - set pa_error=True
      - set deterministic_fallback_used=True
      - set firewall_passed=False
      - return the deterministic_rationale unchanged

    The LLM must NOT be called when PA compilation fails.
    """
    llm_was_called = []

    def _bad_llm(artifact: Any) -> str:
        llm_was_called.append(True)
        return "LLM rationale that must never be reached."

    # compile_artifact is a deferred local import inside gate(), so we
    # monkeypatch it on the pa_compiler module directly.
    import apps_underwriting_ai.prompt_assembly.underwriting_pa_compiler as pa_mod

    orig_compile = pa_mod.compile_artifact  # type: ignore[attr-defined]

    def _raise(*a: Any, **kw: Any) -> Any:
        raise RuntimeError("Simulated PromptAssemblyError")

    pa_mod.compile_artifact = _raise  # type: ignore[attr-defined]
    try:
        result = _firewall.gate(
            verdict=_VERDICT,
            reason_codes=_REASON_CODES,
            c0_bundle=_C0_BUNDLE,
            deterministic_rationale=_DET_RATIONALE,
            llm_callable=_bad_llm,
        )
    finally:
        pa_mod.compile_artifact = orig_compile  # type: ignore[attr-defined]

    assert result.pa_error is True, (
        "pa_error must be True when PA compilation raises."
    )
    assert result.deterministic_fallback_used is True, (
        "deterministic_fallback_used must be True on PromptAssemblyError."
    )
    assert result.firewall_passed is False, (
        "firewall_passed must be False when PA compilation fails."
    )
    assert result.rationale == _DET_RATIONALE, (
        "The deterministic rationale must be returned unchanged when PA fails."
    )
    assert llm_was_called == [], (
        "The LLM callable MUST NOT be invoked when PA compilation fails."
    )


# ---------------------------------------------------------------------------
# Test 55 — Verdict immutability: firewall blocks when verdict changes
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_verdict_immutability_check_blocks_on_change() -> None:
    """_check_immutability must return (False, 'immutability_verdict_changed')
    when the verdict hash at check-time differs from the compile-time hash.

    This simulates a corrupted or tampered verdict after the PA compilation
    step — the firewall must block and fall back to deterministic rationale.
    """
    original_verdict = "APPROVE"
    original_reason_codes = ["RC000_CREDIT_SCORE_STRONG"]

    original_verdict_hash = _hash(original_verdict)
    original_reason_codes_hash = _hash(sorted(original_reason_codes))

    # Tamper: use a DIFFERENT verdict hash (as if something changed the verdict).
    tampered_verdict_hash = _hash("DECLINE")

    ok, reason = _check_immutability(
        original_verdict=original_verdict,
        original_reason_codes=original_reason_codes,
        original_verdict_hash=tampered_verdict_hash,   # tampered!
        original_reason_codes_hash=original_reason_codes_hash,
    )

    assert ok is False, (
        "Immutability check must return ok=False when verdict hash is mismatched."
    )
    assert reason == "immutability_verdict_changed", (
        f"failure reason must be 'immutability_verdict_changed', got {reason!r}."
    )

    # Confirm clean case passes.
    ok_clean, reason_clean = _check_immutability(
        original_verdict=original_verdict,
        original_reason_codes=original_reason_codes,
        original_verdict_hash=original_verdict_hash,
        original_reason_codes_hash=original_reason_codes_hash,
    )
    assert ok_clean is True, "Clean (unchanged) verdict must pass immutability check."
    assert reason_clean == "none"


# ---------------------------------------------------------------------------
# Test 56 — Reason-codes immutability: firewall blocks when codes change
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_reason_codes_immutability_check_blocks_on_change() -> None:
    """_check_immutability must return (False, 'immutability_reason_codes_changed')
    when the reason_codes hash at check-time differs from the compile-time hash.
    """
    original_verdict = "REFER"
    original_reason_codes = ["RC003_DEBT_SERVICE_CAPACITY_LOW"]

    original_verdict_hash = _hash(original_verdict)
    original_reason_codes_hash = _hash(sorted(original_reason_codes))

    # Tamper: use a different reason_codes hash (as if LLM injected a new code).
    tampered_rc_hash = _hash(sorted(["RC003_DEBT_SERVICE_CAPACITY_LOW", "RC_INVENTED"]))

    ok, reason = _check_immutability(
        original_verdict=original_verdict,
        original_reason_codes=original_reason_codes,
        original_verdict_hash=original_verdict_hash,
        original_reason_codes_hash=tampered_rc_hash,  # tampered!
    )

    assert ok is False, (
        "Immutability check must return ok=False when reason_codes hash is mismatched."
    )
    assert reason == "immutability_reason_codes_changed", (
        f"failure reason must be 'immutability_reason_codes_changed', got {reason!r}."
    )


# ---------------------------------------------------------------------------
# Test 57 — LLM callable exception → deterministic fallback
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_llm_callable_exception_triggers_fallback() -> None:
    """When the llm_callable raises an exception, the firewall must:
      - return deterministic_fallback_used=True
      - return firewall_passed=False
      - return failure_reason='llm_callable_exception'
      - return the deterministic_rationale unchanged

    PA compilation must still have succeeded (pa_error=False).
    """
    def _crashing_llm(artifact: Any) -> str:
        raise RuntimeError("Simulated LLM provider error")

    result = _firewall.gate(
        verdict=_VERDICT,
        reason_codes=_REASON_CODES,
        c0_bundle=_C0_BUNDLE,
        deterministic_rationale=_DET_RATIONALE,
        request_id="req-fw-crash",
        llm_callable=_crashing_llm,
    )

    assert result.deterministic_fallback_used is True, (
        "deterministic_fallback_used must be True when llm_callable raises."
    )
    assert result.firewall_passed is False, (
        "firewall_passed must be False when llm_callable raises."
    )
    assert result.failure_reason == "llm_callable_exception", (
        f"failure_reason must be 'llm_callable_exception', got {result.failure_reason!r}."
    )
    assert result.rationale == _DET_RATIONALE, (
        "Deterministic rationale must be returned unchanged when LLM callable fails."
    )
    assert result.pa_error is False, (
        "pa_error must be False — PA compiled successfully before the LLM call."
    )
    assert result.immutability_violation is False, (
        "No immutability violation should be flagged for an LLM exception."
    )


# ---------------------------------------------------------------------------
# Test 58 — Accepted LLM rationale returned as-is; verdict + reason_codes unchanged
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_accepted_llm_rationale_returned_verdict_unchanged() -> None:
    """When the llm_callable returns valid rationale, the firewall must:
      - return firewall_passed=True
      - return deterministic_fallback_used=False
      - return the exact LLM rationale string
      - leave verdict and reason_codes completely unchanged
      - set immutability_violation=False

    This test also verifies that the artifact_hash is non-empty (proving
    PA compiled before the LLM call) and that audit_refs are populated.
    """
    _LLM_RATIONALE = (
        "The application demonstrates strong creditworthiness with 3 verified "
        "evidence records, 7 derived risk features, and zero unresolved "
        "document reconciliations. The APPROVE verdict is supported by "
        "all required documentation."
    )

    def _good_llm(artifact: Any) -> str:
        # Verify the artifact has the expected hash bindings.
        assert artifact.verdict_hash == _hash(_VERDICT), (
            "LLM callable must receive an artifact with the correct verdict_hash."
        )
        assert artifact.reason_codes_hash == _hash(sorted(_REASON_CODES)), (
            "LLM callable must receive an artifact with the correct reason_codes_hash."
        )
        assert artifact.verdict_locked is True, "artifact.verdict_locked must be True."
        assert artifact.reason_codes_locked is True, "artifact.reason_codes_locked must be True."
        return _LLM_RATIONALE

    verdict_before = _VERDICT
    reason_codes_before = list(_REASON_CODES)

    result = _firewall.gate(
        verdict=_VERDICT,
        reason_codes=_REASON_CODES,
        c0_bundle=_C0_BUNDLE,
        deterministic_rationale=_DET_RATIONALE,
        request_id="req-fw-accept",
        llm_callable=_good_llm,
    )

    assert result.firewall_passed is True, (
        f"firewall_passed must be True for a clean LLM pass, "
        f"got failure_reason={result.failure_reason!r}."
    )
    assert result.deterministic_fallback_used is False, (
        "deterministic_fallback_used must be False when LLM succeeds."
    )
    assert result.rationale == _LLM_RATIONALE, (
        "The accepted LLM rationale must be returned exactly as-is."
    )
    assert result.immutability_violation is False, (
        "No immutability violation should be flagged for a clean LLM pass."
    )
    assert result.artifact_hash != "", (
        "artifact_hash must be non-empty, proving PA compiled before the LLM call."
    )
    assert len(result.audit_refs) > 0, (
        "audit_refs must be populated by the PA compiler."
    )

    # Verify verdict and reason_codes are completely unchanged after firewall.
    assert _VERDICT == verdict_before, (
        "Firewall must not mutate the verdict variable."
    )
    assert _REASON_CODES == reason_codes_before, (
        "Firewall must not mutate the reason_codes list."
    )
    assert result.failure_reason == "none", (
        f"failure_reason must be 'none' on accepted LLM rationale, got {result.failure_reason!r}."
    )
