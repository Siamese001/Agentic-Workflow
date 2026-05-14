"""C0 binding — adapts AppIngressRunner route+validated to apps_qna C0 adapter.

AppIngressRunner calls: fec = c0(route, validated)
  — only when route.grounding_required is True.

Consumes: QnaRouteContract (route), ValidatedRequest (validated)
Emits:    dict — FinalEvidenceContract-shaped dict from apps_qna.c0_adapter.call_c0()

The result is passed downstream to pa_fn(route, l1_plan, fec, validated).
AppIngressRunner treats the fec as opaque — it is forwarded to pa_fn.

Plan: .windsurf/plans/one-spine-qna-rfp-migration-d2e8f1.md W1.P1
"""
from __future__ import annotations

import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


def qna_c0(route: Any, validated: Any) -> dict[str, Any]:
    """C0 stage binding for apps_qna.

    Extracts interview_slug from the ValidatedRequest and calls the canonical
    apps_qna C0 adapter. Fail-closed: C0UnavailableError propagates.

    Args:
        route: QnaRouteContract from qna_l0.
        validated: ValidatedRequest from qna_u0.

    Returns:
        FinalEvidenceContract-shaped dict.

    Raises:
        C0UnavailableError: If canonical C0 is unreachable (fail-closed).
    """
    from apps_qna.c0_adapter import call_c0

    route_id: str = getattr(route, "route_id", "") or ""
    # ValidatedRequest.batch_id carries the interview_slug (set by qna_u0)
    interview_slug: str = getattr(validated, "batch_id", "") or ""

    _LOGGER.debug("qna_c0: slug=%s route_id=%s", interview_slug, route_id)

    return call_c0(
        interview_slug=interview_slug,
        route_id=route_id,
        query_text=interview_slug,
    )


__all__ = ["qna_c0"]
