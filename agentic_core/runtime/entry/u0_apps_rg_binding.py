"""U0 ingress validator binding for the apps_rg `resume_generation` task class.

Per plan apps-rg-u0-reflection-live-wiring-105147 W1.P1.2 (supersedes the
W3.P1 thin binding from plan apps-rg-runtime-wiring-completion-d4e8a1).

U0 is the FIRST stage of the U0 -> L1 -> L0 -> [C0] -> [PA] -> L2 -> Exit
pipeline. Its job is to:

    1. Synthesize an AppsRgIngressContractV1-shaped JSON dict from the
       legacy thin RequestEnvelope (transitional bridge until apps_rg/
       __main__.py emits the contract directly — see
       agentic_core/runtime/u0/payload_synthesizer.py).
    2. Run apps_rg_u0_adapt over that JSON — validates schema, enforces
       jd_hash / replay_key / generation_mode / policy refs, walks every
       JSON Pointer through the field-map SSOT, fails closed on any
       silently_dropped or unknown_mappings.
    3. Run the legacy AppsRgRuntimeAuthorityPolicy.validate_ingress_payload
       scan as a defence-in-depth check against forbidden authority fields.
    4. Return a ValidatedRequest carrying:
         - the harness's app_payload (full domain content under app_payload)
         - the reflection_receipt (proof of pointer coverage)
         - audit_refs entry "reflection:<input_payload_digest[:16]>" so the
           existing audit chain captures the harness verdict
         - the legacy AuthorityValidationReceipt (forbidden-fields scan)

The harness is now MANDATORY on the live runtime path. Any caller that
reaches L1 with a ValidatedRequest produced by this binding has been
through the full reflection check.

Pattern: pure function. No state. No I/O beyond the synthesizer's
deterministic resume/JD text reads (already restricted to declared paths).
No provider calls.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    RequestEnvelope,
    ValidatedRequest,
)
from agentic_core.runtime.contracts.apps_rg_runtime_authority_policy import (
    AppsRgAuthorityViolation,
    AppsRgRuntimeAuthorityPolicy,
    AuthorityValidationReceipt,
)
from agentic_core.runtime.u0.apps_rg_u0_adapter import apps_rg_u0_adapt
from agentic_core.runtime.u0.payload_synthesizer import synthesize_contract_payload


# Task class identifier — bound to apps_rg by U0 (immutable string).
APPS_RG_TASK_CLASS: str = "resume_generation"

# L5 certification reference for the U0 binding stage. Updated to record
# that the harness is now on the live path.
APPS_RG_U0_CERT_REF: str = "u0-apps-rg-resume-generation-reflection-live-105147"


def u0_validate_apps_rg(envelope: RequestEnvelope) -> ValidatedRequest:
    """Validate an apps_rg RequestEnvelope and produce a ValidatedRequest.

    Pipeline:
        1. Synthesize AppsRgIngressContractV1 JSON from envelope (bridge).
        2. Run apps_rg_u0_adapt — schema + reflection + domain checks.
        3. Run legacy authority-fields scan (defence in depth).
        4. Merge into a single ValidatedRequest carrying:
            - app_payload (from harness)
            - reflection_receipt (from harness)
            - authority_validation_receipt (from legacy scan)
            - audit_refs += ("reflection:<digest_prefix>",)

    Args:
        envelope: The RequestEnvelope built by apps_rg_parse from the
            CLI/wizard payload dict.

    Returns:
        ValidatedRequest carrying the AuthorityValidationReceipt, the
        AppsRgU0ReflectionReceipt, the full apps_rg payload under
        app_payload, and the digests required for downstream replay.

    Raises:
        AppsRgU0AdapterError (and subclasses): if the synthesized contract
            fails schema validation, domain checks, or pointer reflection.
            All are fail-closed signals — the request must NOT proceed
            past U0.
        AppsRgAuthorityViolation: if the payload contains a forbidden
            authority field (legacy scan; harness's contract already
            forbids these structurally).
        TypeError: if envelope is not a RequestEnvelope (defensive).
    """

    if not isinstance(envelope, RequestEnvelope):
        raise TypeError(
            f"u0_validate_apps_rg expected RequestEnvelope, got {type(envelope).__name__}"
        )

    # 1. Synthesize the contract-shaped JSON. Pure function — deterministic.
    contract_json = synthesize_contract_payload(envelope)

    # 2. Run the contract-first reflection harness. Raises on any of:
    #    MissingJdHashError, InvalidJdPayloadError, MissingReplayKeyError,
    #    UnknownGenerationModeError, MissingPolicyRefsError,
    #    SilentlyDroppedFieldError, UnknownFieldMappingError, or generic
    #    AppsRgU0AdapterError. All are fail-closed before L1.
    harness_validated, reflection_receipt = apps_rg_u0_adapt(
        contract_json,
        request_id=envelope.request_id,
        run_id=envelope.run_id,
    )

    # 3. Defence-in-depth: legacy forbidden-fields scan over the original
    #    AppsRgIngressPayload dataclass. The harness's contract already
    #    forbids these structurally (extra='forbid' on Pydantic model), but
    #    a future caller that reconstructs the envelope without going
    #    through the harness would miss that — keep this as a belt.
    timestamp_iso = envelope.submitted_at or datetime.now(timezone.utc).isoformat()
    legacy_receipt: AuthorityValidationReceipt = (
        AppsRgRuntimeAuthorityPolicy.validate_ingress_payload(
            payload=envelope.payload,
            request_id=envelope.request_id,
            timestamp_iso=timestamp_iso,
        )
    )
    if not legacy_receipt.allowed:
        raise AppsRgAuthorityViolation(
            f"U0 (legacy authority scan) rejected apps_rg payload "
            f"(request_id={envelope.request_id}): forbidden fields detected: "
            f"{legacy_receipt.forbidden_fields_detected}. apps_rg has no runtime "
            "authority — these fields must be removed from the ingress payload."
        )

    # 4. Merge: take harness's ValidatedRequest as the base (it carries
    #    app_payload + correct digests), then thread the reflection receipt,
    #    audit ref, and legacy authority receipt through it.
    digest_prefix = reflection_receipt.input_payload_digest[:16]
    merged_audit_refs: tuple[str, ...] = (
        *harness_validated.audit_refs,
        f"reflection:{digest_prefix}",
    )

    return replace(
        harness_validated,
        authority_validation_receipt=legacy_receipt,
        audit_refs=merged_audit_refs,
        reflection_receipt=reflection_receipt,
        l5_certification_ref=APPS_RG_U0_CERT_REF,
    )


__all__ = [
    "APPS_RG_TASK_CLASS",
    "APPS_RG_U0_CERT_REF",
    "u0_validate_apps_rg",
]
