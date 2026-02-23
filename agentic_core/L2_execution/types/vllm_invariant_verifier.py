"""
PHASE 5 — Formal Invariant Verifier: Runtime Enforcement Implementation.

Verifies architectural invariants at the execution boundary (Phase 3 adapter/controller seam).
All violations are deterministic and canonically serializable.

No GPU libraries. No torch/vllm imports. L2 purity preserved.
"""

from __future__ import annotations

from typing import Any


def verify_gateway_invariants(
    *,
    provider_selected: str,
    local_request: Any | None,
    telemetry_dict: dict[str, Any],
    fingerprint: Any | None,
) -> list[InvariantViolation]:
    """
    Verify architectural invariants at the gateway execution boundary.

    Args:
        provider_selected: Selected provider (e.g., "Qwen2.5-7B-Instruct" or "gemini-2.5-pro").
        local_request: Shaped local request (None if routed to Gemini).
        telemetry_dict: Telemetry dictionary with stable key ordering.
        fingerprint: Infrastructure fingerprint (None if not provided).

    Returns:
        List of InvariantViolation objects, sorted by invariant_id then severity.
    """
    # Function-scoped imports to avoid lazy seam violations
    from agentic_core.L2_execution.types.vllm_invariant_contract import (
        InvariantId,
        InvariantSeverity,
        InvariantViolation,
    )

    violations: list[InvariantViolation] = []

    # INV_LOCAL_REQUEST_HAS_EXPLICIT_MAX_TOKENS
    if local_request is not None:
        max_tokens = getattr(local_request, "max_tokens", None)
        if max_tokens is None:
            violations.append(
                InvariantViolation(
                    invariant_id=InvariantId.INV_LOCAL_REQUEST_HAS_EXPLICIT_MAX_TOKENS.value,
                    severity=InvariantSeverity.FAIL.value,
                    message="Local request missing explicit max_tokens",
                    context={"provider": provider_selected},
                )
            )

    # INV_LOCAL_REQUEST_TEMPERATURE_ZERO
    if local_request is not None:
        temperature = getattr(local_request, "temperature", None)
        if temperature is not None and temperature != 0.0:
            violations.append(
                InvariantViolation(
                    invariant_id=InvariantId.INV_LOCAL_REQUEST_TEMPERATURE_ZERO.value,
                    severity=InvariantSeverity.FAIL.value,
                    message=f"Local request temperature must be 0.0 for determinism, got {temperature}",
                    context={"provider": provider_selected, "temperature": temperature},
                )
            )

    # INV_LOCAL_REQUEST_SEED_PRESENT
    if local_request is not None:
        seed = getattr(local_request, "seed", None)
        if seed is None:
            violations.append(
                InvariantViolation(
                    invariant_id=InvariantId.INV_LOCAL_REQUEST_SEED_PRESENT.value,
                    severity=InvariantSeverity.FAIL.value,
                    message="Local request missing seed for deterministic replay",
                    context={"provider": provider_selected},
                )
            )

    # INV_TELEMETRY_HAS_FINGERPRINT_HASH
    fingerprint_hash = telemetry_dict.get("fingerprint_hash")
    if not fingerprint_hash:
        violations.append(
            InvariantViolation(
                invariant_id=InvariantId.INV_TELEMETRY_HAS_FINGERPRINT_HASH.value,
                severity=InvariantSeverity.FAIL.value,
                message="Telemetry missing fingerprint_hash for replay sealing",
                context={"provider": provider_selected},
            )
        )

    # INV_GEMINI_FALLBACK_REQUIRES_REASON
    if "gemini" in provider_selected.lower():
        failure_type = telemetry_dict.get("failure_type")
        if not failure_type:
            violations.append(
                InvariantViolation(
                    invariant_id=InvariantId.INV_GEMINI_FALLBACK_REQUIRES_REASON.value,
                    severity=InvariantSeverity.FAIL.value,
                    message="Gemini fallback requires explicit failure_type",
                    context={"provider": provider_selected},
                )
            )

    # Sort violations by invariant_id then severity for deterministic ordering
    violations.sort(key=lambda v: (v.invariant_id, v.severity))

    return violations
