"""U0 binding — adapts AppIngressRunner envelope to apps_rfp U0 intake.

AppIngressRunner calls: validated = u0(envelope)

Consumes: RequestEnvelope (from profile_builder.parse_payload)
Emits:    ValidatedRequest (from agentic_core.L0_routing.intake.validated_request)

Extracts rfp_document_path and target_company from the envelope payload and
produces a ValidatedRequest stamped for apps_rfp proposal assembly.

Plan: .windsurf/plans/one-spine-qna-rfp-migration-d2e8f1.md W2.P1
"""
from __future__ import annotations

import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


def rfp_u0(envelope: Any) -> Any:
    """U0 stage binding for apps_rfp.

    Extracts rfp_document_path / target_company from the RequestEnvelope payload
    and delegates to apps_rfp.u0_intake.intake_rfp_request() to produce a
    fully-populated ValidatedRequest for the agentic_core spine.

    Args:
        envelope: RequestEnvelope from profile_builder.parse_payload.

    Returns:
        ValidatedRequest stamped for apps_rfp proposal_assembly runtime.

    Raises:
        ValueError: If neither rfp_document_path nor target_company can be resolved.
    """
    from apps_rfp.u0_intake import intake_rfp_request

    payload = getattr(envelope, "payload", None)
    rfp_document_path: str = ""
    target_company: str = ""
    dry_run: bool = False

    if payload is not None:
        constraints = getattr(payload, "user_constraints", None) or {}
        if isinstance(constraints, dict):
            rfp_document_path = constraints.get("rfp_document_path", "") or ""
        target_company = getattr(payload, "target_company", "") or ""
        dry_run = bool(getattr(payload, "dry_run", False))

    # Also check raw envelope fields for direct dict payloads
    if not rfp_document_path:
        rfp_document_path = getattr(envelope, "rfp_document_path", "") or ""
    if not target_company:
        target_company = getattr(envelope, "target_company", "") or ""
    if not dry_run:
        dry_run = bool(getattr(envelope, "dry_run", False))

    request_id: str | None = getattr(envelope, "request_id", None) or None
    run_id: str | None = getattr(envelope, "run_id", None) or None
    tenant_id: str = getattr(envelope, "tenant_id", None) or "apps_rfp"
    trace_id: str = getattr(envelope, "trace_id", None) or ""

    _LOGGER.debug(
        "rfp_u0: rfp_document_path=%s target_company=%s request_id=%s dry_run=%s",
        rfp_document_path,
        target_company,
        request_id,
        dry_run,
    )

    return intake_rfp_request(
        rfp_document_path=rfp_document_path,
        target_company=target_company,
        request_id=request_id,
        run_id=run_id,
        tenant_id=tenant_id,
        trace_id=trace_id,
        dry_run=dry_run,
    )


__all__ = ["rfp_u0"]
