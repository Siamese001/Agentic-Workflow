"""C0 Thin Adapter — shapes request, calls canonical C0, returns unchanged.

W0 thin-slice: minimal adapter that returns a mock/stub
FinalEvidenceContract. Full implementation lands in W2.1 with
canonical C0 integration.

The adapter MUST:
- Shape an app-specific C0 request from interview parameters
- Call the canonical C0 retrieval endpoint
- Return the canonical FinalEvidenceContract unchanged
- Handle C0 errors fail-closed (→ SAFE_ABSTAIN)
- Never transform evidence or invent facts

Plan: .windsurf/plans/apps-qna-spine-integration-e9c5b3.md W0.2
"""

from __future__ import annotations

import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


def call_c0(
    *,
    interview_slug: str,
    route_id: str,
    query_text: str = "",
) -> dict[str, Any]:
    """Call canonical C0 and return FinalEvidenceContract unchanged.

    W0: returns a stub contract. W2.1 replaces with real C0 call.

    Args:
        interview_slug: The interview slug for evidence scoping.
        route_id: The selected route id.
        query_text: Optional retrieval query text.

    Returns:
        A FinalEvidenceContract-shaped dict.
    """
    return {
        "schema_version": "1.0",
        "producer": "agentic_core.C0.stub",
        "grounded": True,
        "retrieval_sources": [],
        "route_id": route_id,
        "evidence_sufficiency": "grounded",
        "interview_slug": interview_slug,
        "query_text": query_text,
        "_stub": True,
    }


__all__ = ["call_c0"]
