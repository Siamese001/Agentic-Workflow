"""U0 binding — adapts AppIngressRunner envelope to apps_qna U0 intake.

AppIngressRunner calls: validated = u0(envelope)

The envelope is a RequestEnvelope produced by profile_builder.parse_payload.
This binding extracts the interview_slug from the payload and delegates to
the canonical apps_qna.u0_intake.intake_interview_request().

Consumes: RequestEnvelope
Emits:    ValidatedRequest (from agentic_core.L0_routing.intake.validated_request)

Plan: .windsurf/plans/one-spine-qna-rfp-migration-d2e8f1.md W1.P1
"""
from __future__ import annotations

import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


def qna_u0(envelope: Any) -> Any:
    """U0 stage binding for apps_qna.

    Extracts interview_slug from the RequestEnvelope payload and produces a
    ValidatedRequest via apps_qna.u0_intake.intake_interview_request().

    Args:
        envelope: RequestEnvelope from profile_builder.parse_payload.

    Returns:
        ValidatedRequest stamped for live interview runtime.

    Raises:
        ValueError: If interview_slug cannot be resolved from the envelope.
    """
    from apps_qna.u0_intake import intake_interview_request

    # RequestEnvelope carries an AppsRgIngressPayload in .payload
    # The interview_slug is stored in .payload.user_constraints["interview_slug"]
    # or can be resolved from .payload.target_role as a fallback.
    payload = getattr(envelope, "payload", None)
    interview_slug: str = ""

    if payload is not None:
        constraints = getattr(payload, "user_constraints", None) or {}
        interview_slug = (
            constraints.get("interview_slug", "")
            if isinstance(constraints, dict)
            else getattr(constraints, "interview_slug", "")
        ) or ""
        if not interview_slug:
            # Fallback: target_role used as slug when no explicit slug
            interview_slug = getattr(payload, "target_role", "") or ""

    if not interview_slug:
        raise ValueError(
            "qna_u0: cannot resolve interview_slug from envelope. "
            "profile_builder.parse_payload must set user_constraints['interview_slug']."
        )

    request_id = getattr(envelope, "request_id", None) or None
    _LOGGER.debug("qna_u0: slug=%s request_id=%s", interview_slug, request_id)

    return intake_interview_request(
        interview_slug=interview_slug,
        request_id=request_id,
        briefing_path=None,
    )


__all__ = ["qna_u0"]
