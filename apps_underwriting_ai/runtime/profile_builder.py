"""apps_underwriting_ai profile builder — Bundle B canonical form.

Builds AppRuntimeProfile for apps_underwriting_ai with all 7 stage
binding refs wired. AppIngressRunner(profile=profile).run(payload)
sequences those refs directly; underwriting_dispatch is NOT imported
or referenced here.

No app-specific logic may be added to agentic_core in exchange for this file.
This module is the boundary: everything apps_underwriting_ai-specific lives
here or in apps_underwriting_ai.runtime.bindings.

Required fields for the underwriting domain:
    applicant_id, product_class
The raw payload also carries documents (list) and metadata (dict).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4

from agentic_core.runtime.entry.app_ingress_runner import AppRuntimeProfile
from apps_underwriting_ai.runtime.bindings import (
    u0_validate_underwriting,
    l1_plan_underwriting,
    l0_route_underwriting,
    c0_run_underwriting,
    pa_compose_underwriting_profile,
    l2_execute_underwriting,
    exit_finalize_underwriting,
)
from apps_underwriting_ai.runtime.contracts.underwriting_ingress_payload import (
    UnderwritingIngressEnvelope,
)

UW_REQUIRED_FIELDS: tuple[str, ...] = (
    "applicant_id",
    "product_class",
)


def parse_payload(payload: Mapping[str, Any]) -> UnderwritingIngressEnvelope | None:
    """Convert a normalized payload dict into an UnderwritingIngressEnvelope.

    Signature matches AppRuntimeProfile.parse:
        (payload: Mapping[str, Any]) -> UnderwritingIngressEnvelope | None
    Returns None when payload cannot be parsed (surfaces ClarificationRequired).
    """
    if not isinstance(payload, dict):
        return None

    applicant_id = payload.get("applicant_id") or None
    product_class = payload.get("product_class") or None

    if not applicant_id or not product_class:
        return None

    documents_raw = payload.get("documents") or []
    if not isinstance(documents_raw, (list, tuple)):
        documents_raw = []
    documents: tuple[dict[str, Any], ...] = tuple(
        d for d in documents_raw if isinstance(d, dict)
    )

    metadata = payload.get("metadata") or {}
    if not isinstance(metadata, dict):
        metadata = {}

    try:
        return UnderwritingIngressEnvelope(
            request_id=str(payload.get("request_id") or f"uw-req-{uuid4().hex[:12]}"),
            applicant_id=str(applicant_id),
            product_class=str(product_class),
            documents=documents,
            metadata=metadata,
            trace_id=str(payload.get("trace_id") or f"uw-trace-{uuid4().hex[:16]}"),
            submitted_at=str(
                payload.get("submitted_at") or datetime.now(timezone.utc).isoformat()
            ),
        )
    except (TypeError, ValueError):  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
        return None


def build_app_runtime_contract() -> AppRuntimeProfile:
    """Construct and return the canonical AppRuntimeProfile for apps_underwriting_ai.

    All 7 stage binding refs are wired here. AppIngressRunner sequences
    them directly via _run_profile_stages(); underwriting_dispatch is not
    involved.

    Stage mapping:
        u0   = u0_validate_underwriting     (validates envelope → ValidatedUnderwritingRequest)
        l1   = l1_plan_underwriting         (pass-through → UWL1Plan)
        l0   = l0_route_underwriting        (fixed route → UWRoute; grounding_required=True)
        c0   = c0_run_underwriting          (C0 + 5×L2 deterministic pipeline → UWEvidenceResult)
        pa   = pa_compose_underwriting_profile  (adapts UWEvidenceResult → compiled prompt dict)
        l2   = l2_execute_underwriting      (LLM rationale call → UWSealedArtifact)
        exit = exit_finalize_underwriting   (ExitFecProducer → UWExitResult)

    AppIngressRunner will populate profile_digest and binding_digest_map
    before any stage is called; do not pre-populate those fields here.

    Returns
    -------
    AppRuntimeProfile
        Ready to pass as AppIngressRunner(profile=profile).run(payload).
    """
    return AppRuntimeProfile(
        app_id="apps_underwriting_ai",
        required_fields=UW_REQUIRED_FIELDS,
        parse=parse_payload,
        u0=u0_validate_underwriting,
        l1=l1_plan_underwriting,
        l0=l0_route_underwriting,
        c0=c0_run_underwriting,
        pa=pa_compose_underwriting_profile,
        l2=l2_execute_underwriting,
        exit=exit_finalize_underwriting,
        profile_version="1",
    )


__all__ = [
    "UW_REQUIRED_FIELDS",
    "build_app_runtime_contract",
    "parse_payload",
]
