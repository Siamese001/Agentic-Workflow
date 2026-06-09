"""R1B Semantic Cache — advisory-only, never silent terminal return.

W4.3: Semantic similarity cache that provides advisory suggestions only.
Must never silently return a result as authoritative. Always marked
as advisory with confidence score.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-qna-spine-integration-e9c5b3.md W4.3
"""

from __future__ import annotations

from typing import Any

_CACHE_NAMESPACE = "apps_qna.r1b_semantic"
_TENANT_ID = "apps_qna"
_WARNING = "R1B is advisory-only; never use as authoritative cache hit."
_L4_CACHE_EXCEPTIONS = (ImportError, AttributeError, RuntimeError, ValueError, OSError)


def _query_context(*, interview_slug: str, query_text: str = "") -> str:
    """Build the stable L4 recall context for apps_qna R1B probes."""
    query = (query_text or "").strip()
    slug = (interview_slug or "").strip()
    return query or slug


def _get_semantic_cache_manager() -> Any:
    from agentic_core.L4_state.utils.memory.semantic_cache_manager import (  # noqa: PLC0415
        SemanticCacheManager,
    )

    return SemanticCacheManager.get_instance()


def _confidence_from_payload(payload: dict[str, Any] | None) -> float:
    if not isinstance(payload, dict):
        return 0.0
    for key in ("confidence", "score", "support_score"):
        value = payload.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return 0.0


def _advisory_response(
    *,
    interview_slug: str,
    query_text: str,
    context: str,
    cache_hit: bool,
    cache_status: str,
    suggestion: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "advisory": True,
        "interview_slug": interview_slug,
        "query_text": query_text,
        "context": context,
        "cache_namespace": _CACHE_NAMESPACE,
        "cache_status": cache_status,
        "cache_hit": cache_hit,
        "confidence": _confidence_from_payload(suggestion),
        "result": None,
        "suggestion": suggestion,
        "warning": _WARNING,
    }


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
    context = _query_context(interview_slug=interview_slug, query_text=query_text)
    if not context:
        return _advisory_response(
            interview_slug=interview_slug,
            query_text=query_text,
            context=context,
            cache_hit=False,
            cache_status="empty_context",
        )

    try:
        cache = _get_semantic_cache_manager()
        suggestion = cache.recall(
            context,
            _CACHE_NAMESPACE,
            tenant_id=_TENANT_ID,
            flow_class="R1B_READ",
        )
    except _L4_CACHE_EXCEPTIONS:
        return _advisory_response(
            interview_slug=interview_slug,
            query_text=query_text,
            context=context,
            cache_hit=False,
            cache_status="unavailable",
        )

    if not isinstance(suggestion, dict):
        suggestion = None

    return _advisory_response(
        interview_slug=interview_slug,
        query_text=query_text,
        context=context,
        cache_hit=suggestion is not None,
        cache_status="hit" if suggestion is not None else "miss",
        suggestion=suggestion,
    )


__all__ = ["r1b_lookup"]
