"""LLM Rationale Firewall for apps_underwriting_ai.

Enforces the LLM firewall contract declared in the spine plan (W4.1):

  1. PA compiler runs BEFORE any provider call.
  2. `verdict` and `reason_codes` are hashed into the CompiledPromptArtifact
     BEFORE the LLM call — any post-call change is detectable.
  3. Post-call immutability check: if the LLM output changes verdict or
     reason_codes, the output is rejected and the deterministic fallback is used.
  4. On `PromptAssemblyError` → deterministic_rationale_fallback_used=True.

Responsibility matrix:
  - DeterministicRiskScorer **owns**: verdict, reason_codes — IMMUTABLE after lock.
  - LLM lane **owns only**: plain-English rationale prose.
  - PA compiler **owns**: slot assembly, hash binding, firewall enforcement.
  - LLMFirewall **owns**: pre-call PA compilation, post-call immutability check,
                          fallback routing, telemetry emission.

This module MUST NOT:
  - change verdict or reason_codes
  - perform open-web retrieval
  - write to L4 state
  - emit Exit disposition

Plan: apps-underwriting-ai-spine-hardening-d7f3b2 W4.1.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from typing import Any

_LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FIREWALL_MODE_STRICT = "strict"
FIREWALL_MODE_ADVISORY = "advisory"

# Environment bypass — mirrors the existing APPS_UW_RATIONALE_LLM_DISABLED flag.
_ENV_FIREWALL_DISABLED = "APPS_UW_FIREWALL_DISABLED"

# Default template to use when caller does not specify.
_DEFAULT_TEMPLATE_ID = "decision_rationale_enrichment_v1"


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class FirewallResult:
    """Result of a single LLM firewall pass.

    Fields:
      rationale: Final rationale string (LLM or deterministic fallback).
      deterministic_fallback_used: True when the PA compiler or post-call
        check forced fallback to the deterministic rationale.
      firewall_passed: True when PA compiled successfully and post-call
        immutability check passed.
      artifact_id: CompiledPromptArtifact ID, or '' if compilation failed.
      artifact_hash: Hash of the compiled artifact, or '' on failure.
      verdict_hash: Hash of the verdict bound at compile time.
      reason_codes_hash: Hash of the reason codes bound at compile time.
      failure_reason: Human-readable reason for fallback, or 'none'.
      pa_error: True when PromptAssemblyError was raised during compilation.
      immutability_violation: True when LLM output tried to change verdict or codes.
    """

    rationale: str
    deterministic_fallback_used: bool
    firewall_passed: bool
    artifact_id: str = ""
    artifact_hash: str = ""
    verdict_hash: str = ""
    reason_codes_hash: str = ""
    failure_reason: str = "none"
    pa_error: bool = False
    immutability_violation: bool = False
    audit_refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rationale": self.rationale,
            "deterministic_fallback_used": self.deterministic_fallback_used,
            "firewall_passed": self.firewall_passed,
            "artifact_id": self.artifact_id,
            "artifact_hash": self.artifact_hash,
            "verdict_hash": self.verdict_hash,
            "reason_codes_hash": self.reason_codes_hash,
            "failure_reason": self.failure_reason,
            "pa_error": self.pa_error,
            "immutability_violation": self.immutability_violation,
            "audit_refs": self.audit_refs,
        }


# ---------------------------------------------------------------------------
# Hash helper (mirrors PA compiler's _compute_hash)
# ---------------------------------------------------------------------------

def _hash(data: Any) -> str:
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Immutability check
# ---------------------------------------------------------------------------

def _check_immutability(
    *,
    original_verdict: str,
    original_reason_codes: list[str],
    original_verdict_hash: str,
    original_reason_codes_hash: str,
) -> tuple[bool, str]:
    """Verify that verdict and reason_codes have not changed post-LLM.

    Returns (ok, failure_reason). ok=True means no violation.
    """
    current_verdict_hash = _hash(original_verdict)
    current_reason_codes_hash = _hash(sorted(original_reason_codes))

    if current_verdict_hash != original_verdict_hash:
        return False, "immutability_verdict_changed"
    if current_reason_codes_hash != original_reason_codes_hash:
        return False, "immutability_reason_codes_changed"
    return True, "none"


# ---------------------------------------------------------------------------
# Core firewall class
# ---------------------------------------------------------------------------

class UnderwritingLLMFirewall:
    """LLM firewall gate for the underwriting rationale lane.

    Must be invoked BEFORE any LLM provider call. Wraps the rationale
    enrichment step with:
      1. PA compilation (binds verdict + reason_codes hashes)
      2. Optional LLM call (delegated to caller-supplied callable)
      3. Post-call immutability verification
      4. Deterministic fallback on any failure

    Invariants:
      - NEVER changes verdict or reason_codes
      - NEVER performs retrieval
      - NEVER writes to L4
      - Always returns a FirewallResult — never raises
    """

    def __init__(self, mode: str = FIREWALL_MODE_STRICT) -> None:
        self.mode = mode

    def gate(
        self,
        *,
        verdict: str,
        reason_codes: list[str],
        c0_bundle: dict[str, Any],
        deterministic_rationale: str,
        request_id: str = "",
        run_id: str = "",
        trace_id: str = "",
        template_id: str = _DEFAULT_TEMPLATE_ID,
        llm_callable: Any = None,
        slot_overrides: dict[str, str] | None = None,
    ) -> FirewallResult:
        """Run the full firewall gate sequence.

        Args:
            verdict: Locked verdict string from DeterministicRiskScorer.
            reason_codes: Locked reason code list from DeterministicRiskScorer.
            c0_bundle: FinalEvidenceContract dict from C0 adapter.
            deterministic_rationale: Fallback rationale if firewall blocks.
            request_id: Request ID for tracing.
            run_id: Run ID for this execution.
            trace_id: Trace ID for observability.
            template_id: PA compiler template to use.
            llm_callable: Optional callable(artifact) -> str that invokes LLM.
              If None, returns deterministic_rationale immediately (safe mode).
            slot_overrides: Optional slot overrides forwarded to PA compiler.

        Returns:
            FirewallResult — always, never raises.
        """
        if os.environ.get(_ENV_FIREWALL_DISABLED) == "1":
            return FirewallResult(
                rationale=deterministic_rationale,
                deterministic_fallback_used=True,
                firewall_passed=False,
                failure_reason="firewall_env_disabled",
            )

        artifact_id = f"fw-{uuid.uuid4().hex[:16]}"
        verdict_hash = _hash(verdict)
        reason_codes_hash = _hash(sorted(reason_codes))

        # ------------------------------------------------------------------ #
        # Step 1 — PA compilation (must precede any LLM call)
        # ------------------------------------------------------------------ #
        try:
            import apps_underwriting_ai.prompt_assembly.underwriting_pa_compiler as _pa  # noqa: PLC0415
            PromptAssemblyError = _pa.PromptAssemblyError
            artifact = _pa.compile_artifact(
                template_id=template_id,
                request_id=request_id,
                run_id=run_id,
                trace_id=trace_id,
                artifact_id=artifact_id,
                c0_bundle=c0_bundle,
                verdict=verdict,
                reason_codes=reason_codes,
                slot_overrides=slot_overrides,
            )
        except Exception as exc:  # noqa: BLE001
            # guardian: allow-broad-except -- PA compilation touches disk/yaml/dataclass;
            # any failure must fall through to deterministic rationale (regulated domain floor)
            pa_error = True
            failure_reason = "pa_compilation_error"
            _LOGGER.info(
                "[apps_underwriting_ai] PA firewall compilation failed: %s", exc
            )
            return FirewallResult(
                rationale=deterministic_rationale,
                deterministic_fallback_used=True,
                firewall_passed=False,
                artifact_id=artifact_id,
                verdict_hash=verdict_hash,
                reason_codes_hash=reason_codes_hash,
                failure_reason=failure_reason,
                pa_error=pa_error,
            )

        # Verify the artifact binds the correct verdict and reason_codes hashes.
        if artifact.verdict_hash != verdict_hash:
            return FirewallResult(
                rationale=deterministic_rationale,
                deterministic_fallback_used=True,
                firewall_passed=False,
                artifact_id=artifact_id,
                artifact_hash=artifact.artifact_hash,
                verdict_hash=verdict_hash,
                reason_codes_hash=reason_codes_hash,
                failure_reason="pa_verdict_hash_mismatch",
                pa_error=True,
            )
        if artifact.reason_codes_hash != reason_codes_hash:
            return FirewallResult(
                rationale=deterministic_rationale,
                deterministic_fallback_used=True,
                firewall_passed=False,
                artifact_id=artifact_id,
                artifact_hash=artifact.artifact_hash,
                verdict_hash=verdict_hash,
                reason_codes_hash=reason_codes_hash,
                failure_reason="pa_reason_codes_hash_mismatch",
                pa_error=True,
            )

        # ------------------------------------------------------------------ #
        # Step 2 — LLM call (optional; delegated to caller)
        # ------------------------------------------------------------------ #
        if llm_callable is None:
            return FirewallResult(
                rationale=deterministic_rationale,
                deterministic_fallback_used=True,
                firewall_passed=True,
                artifact_id=artifact_id,
                artifact_hash=artifact.artifact_hash,
                verdict_hash=verdict_hash,
                reason_codes_hash=reason_codes_hash,
                failure_reason="no_llm_callable",
                audit_refs=artifact.audit_refs,
            )

        try:
            llm_rationale: str = llm_callable(artifact)
        except Exception as exc:  # noqa: BLE001
            # guardian: allow-broad-except -- LLM callable failure must fall through
            # to deterministic rationale (regulated domain compliance floor)
            _LOGGER.info(
                "[apps_underwriting_ai] LLM callable failed in firewall: %s", exc
            )
            return FirewallResult(
                rationale=deterministic_rationale,
                deterministic_fallback_used=True,
                firewall_passed=False,
                artifact_id=artifact_id,
                artifact_hash=artifact.artifact_hash,
                verdict_hash=verdict_hash,
                reason_codes_hash=reason_codes_hash,
                failure_reason="llm_callable_exception",
                audit_refs=artifact.audit_refs,
            )

        if not isinstance(llm_rationale, str) or not llm_rationale.strip():
            return FirewallResult(
                rationale=deterministic_rationale,
                deterministic_fallback_used=True,
                firewall_passed=False,
                artifact_id=artifact_id,
                artifact_hash=artifact.artifact_hash,
                verdict_hash=verdict_hash,
                reason_codes_hash=reason_codes_hash,
                failure_reason="llm_empty_response",
                audit_refs=artifact.audit_refs,
            )

        # ------------------------------------------------------------------ #
        # Step 3 — Post-call immutability check
        # ------------------------------------------------------------------ #
        ok, imm_reason = _check_immutability(
            original_verdict=verdict,
            original_reason_codes=reason_codes,
            original_verdict_hash=verdict_hash,
            original_reason_codes_hash=reason_codes_hash,
        )
        if not ok:
            _LOGGER.warning(
                "[apps_underwriting_ai] LLM firewall immutability violation: %s", imm_reason
            )
            return FirewallResult(
                rationale=deterministic_rationale,
                deterministic_fallback_used=True,
                firewall_passed=False,
                artifact_id=artifact_id,
                artifact_hash=artifact.artifact_hash,
                verdict_hash=verdict_hash,
                reason_codes_hash=reason_codes_hash,
                failure_reason=imm_reason,
                immutability_violation=True,
                audit_refs=artifact.audit_refs,
            )

        # ------------------------------------------------------------------ #
        # All checks passed — accept LLM rationale
        # ------------------------------------------------------------------ #
        return FirewallResult(
            rationale=llm_rationale.strip(),
            deterministic_fallback_used=False,
            firewall_passed=True,
            artifact_id=artifact_id,
            artifact_hash=artifact.artifact_hash,
            verdict_hash=verdict_hash,
            reason_codes_hash=reason_codes_hash,
            failure_reason="none",
            audit_refs=artifact.audit_refs,
        )
