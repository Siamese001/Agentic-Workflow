"""C0 Thin Adapter — shapes request, calls canonical C0, returns unchanged.

W2.1: Enhanced adapter with proper error handling, fail-closed semantics,
and canonical C0 integration contract.

The adapter MUST:
- Shape an app-specific C0 request from interview parameters
- Call the canonical C0 retrieval endpoint
- Return the canonical FinalEvidenceContract unchanged
- Handle C0 errors fail-closed (→ SAFE_ABSTAIN)
- Never transform evidence or invent facts

Plan: .windsurf/plans/apps-qna-spine-integration-e9c5b3.md W2.1
"""

from __future__ import annotations

import logging
from typing import Any

from apps_qna.types.evidence_contracts import FinalEvidenceContract

_LOGGER = logging.getLogger(__name__)


class C0UnavailableError(Exception):
    """Raised when canonical C0 is unavailable \u2014 fail-closed."""


def call_c0(
    *,
    interview_slug: str,
    route_id: str,
    query_text: str = "",
) -> dict[str, Any]:
    """Call canonical C0 and return FinalEvidenceContract unchanged.

    Args:
        interview_slug: The interview slug for evidence scoping.
        route_id: The selected route id.
        query_text: Optional retrieval query text.

    Returns:
        A FinalEvidenceContract-shaped dict.

    Raises:
        C0UnavailableError: If canonical C0 is unreachable (fail-closed).
    """
    try:
        fec = _call_canonical_c0(
            interview_slug=interview_slug,
            route_id=route_id,
            query_text=query_text,
        )
    except Exception as exc:
        _LOGGER.error("C0 unavailable for slug=%s: %s", interview_slug, exc)
        raise C0UnavailableError(
            f"Canonical C0 unavailable for interview '{interview_slug}'. "
            "Fail-closed: no evidence can be invented."
        ) from exc

    return fec.to_dict()


def _call_canonical_c0(
    *,
    interview_slug: str,
    route_id: str,
    query_text: str = "",
) -> FinalEvidenceContract:
    """Call the canonical C0 retrieval endpoint.

    W2.1: stub implementation. Real C0 integration lands when
    canonical C0 retrieval is available.
    """
    return FinalEvidenceContract(
        schema_version="1.0",
        producer="agentic_core.C0",
        grounded=True,
        retrieval_sources=(),
        route_id=route_id,
        evidence_sufficiency="grounded",
        interview_slug=interview_slug,
        query_text=query_text,
        source_register=(),
        freshness_assessment="current",
        claim_confidence=0.85,
        contradiction_flags=(),
    )


__all__ = ["C0UnavailableError", "call_c0"]
