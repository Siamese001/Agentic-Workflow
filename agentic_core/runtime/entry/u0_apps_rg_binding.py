"""U0 ingress validator binding for the apps_rg `resume_generation` task class.

Per plan apps-rg-runtime-wiring-completion-d4e8a1 §6 W3.P1.

U0 is the FIRST stage of the U0 -> L1 -> L0 -> [C0] -> [PA] -> L2 -> Exit
pipeline. Its job is to inspect the ingress payload and reject any forbidden
authority fields (route_id, execution_form, provider, prompt_artifact, etc.)
per c8b3e1 §10 / AppsRgRuntimeAuthorityPolicy.FORBIDDEN_PAYLOAD_FIELDS.

This binding is a thin pure function: takes a RequestEnvelope, returns a
ValidatedRequest, raises AppsRgAuthorityViolation on failure.

The heavy lifting (rule definition, payload inspection, receipt construction)
already lives in AppsRgRuntimeAuthorityPolicy.validate_ingress_payload —
this binding just wires it into the apps_rg dispatch chain.

Pattern: pure function. No state. No I/O. No provider calls.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone

from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    AppsRgIngressPayload,
    RequestEnvelope,
    ValidatedRequest,
)
from agentic_core.runtime.contracts.apps_rg_runtime_authority_policy import (
    AppsRgAuthorityViolation,
    AppsRgRuntimeAuthorityPolicy,
    AuthorityValidationReceipt,
)


# Task class identifier — bound to apps_rg by U0 (immutable string).
APPS_RG_TASK_CLASS: str = "resume_generation"

# L5 certification reference for the U0 binding stage. Per
# verify_certification_ref(), any non-empty string is structurally valid;
# semantic checks (expiry, scope, HMAC) are deferred to L5 runtime gates.
# The string identifies WHICH binding stage produced the ValidatedRequest.
APPS_RG_U0_CERT_REF: str = "u0-apps-rg-resume-generation-w3p1"


def _compute_payload_digest(payload: AppsRgIngressPayload) -> str:
    """SHA-256 digest of the ingress payload — supports SealedL2Artifact provenance later."""
    flat = asdict(payload)
    canonical = json.dumps(flat, sort_keys=True, default=str, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def u0_validate_apps_rg(envelope: RequestEnvelope) -> ValidatedRequest:
    """Validate an apps_rg RequestEnvelope and produce a ValidatedRequest.

    Args:
        envelope: The RequestEnvelope built by apps_rg_parse from the
                  CLI payload dict.

    Returns:
        ValidatedRequest carrying the AuthorityValidationReceipt and a
        payload digest for downstream L1/L0/C0/PA/L2/Exit consumption.

    Raises:
        AppsRgAuthorityViolation: if the payload contains any forbidden
            authority field. Per c8b3e1 §10, this is fail-closed: the
            request must NOT proceed past U0.
        TypeError: if envelope is not a RequestEnvelope (defensive).
    """
    if not isinstance(envelope, RequestEnvelope):
        raise TypeError(
            f"u0_validate_apps_rg expected RequestEnvelope, got {type(envelope).__name__}"
        )

    timestamp_iso = envelope.submitted_at or datetime.now(timezone.utc).isoformat()

    receipt: AuthorityValidationReceipt = (
        AppsRgRuntimeAuthorityPolicy.validate_ingress_payload(
            payload=envelope.payload,
            request_id=envelope.request_id,
            timestamp_iso=timestamp_iso,
        )
    )

    if not receipt.allowed:
        raise AppsRgAuthorityViolation(
            f"U0 rejected apps_rg payload (request_id={envelope.request_id}): "
            f"forbidden fields detected: {receipt.forbidden_fields_detected}. "
            "apps_rg has no runtime authority — these fields must be removed "
            "from the ingress payload (see c8b3e1 §10)."
        )

    return ValidatedRequest(
        request_id=envelope.request_id,
        run_id=envelope.run_id,
        app_id="apps_rg",
        task_class=APPS_RG_TASK_CLASS,
        payload_digest=_compute_payload_digest(envelope.payload),
        authority_validation_receipt=receipt,
        trace_id=envelope.trace_id,
        # W1 identity quad (D6): tenant_id sourced from app_id at U0 ingress.
        # Envelope override allowed when the host pre-populated it.
        tenant_id=envelope.tenant_id or "apps_rg",
        # W2: thread target_level for L0 variant routing (DS-3)
        target_level=envelope.payload.target_level or "",
        l5_certification_ref=APPS_RG_U0_CERT_REF,
    )


__all__ = [
    "APPS_RG_TASK_CLASS",
    "APPS_RG_U0_CERT_REF",
    "u0_validate_apps_rg",
]
