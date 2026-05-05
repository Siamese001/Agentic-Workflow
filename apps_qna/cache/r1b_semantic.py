"""R1B Semantic Cache — advisory-only, never silent terminal return.

W4.3: Semantic similarity cache that provides advisory suggestions only.
Must never silently return a result as authoritative. Always marked
as advisory with confidence score.

Plan: .windsurf/plans/apps-qna-spine-integration-e9c5b3.md W4.3
"""

from __future__ import annotations

from typing import Any


def r1b_lookup(
    *,
    interview_slug: str,
    query_text: str = "",
) -> dict[str, Any] | None:
    """Semantic cache lookup — advisory only.

    Args:
        interview_slug: The interview slug.
        query_text: The query text for similarity matching.

    Returns:
        Advisory result dict with confidence, or None.
        Always marked advisory=True — never a silent terminal return.
    """
    return {
        "advisory": True,
        "interview_slug": interview_slug,
        "query_text": query_text,
        "confidence": 0.0,
        "result": None,
        "warning": "R1B is advisory-only; never use as authoritative cache hit.",
    }


__all__ = ["r1b_lookup"]
