"""R1A Exact Cache — requires full digest match for cache hit.

W4.3: Exact-match cache that only returns on full digest equality.
No partial matches, no fuzzy matching. Fail-safe: miss returns None.

Plan: .windsurf/plans/apps-qna-spine-integration-e9c5b3.md W4.3
"""

from __future__ import annotations

import hashlib
from typing import Any

_cache: dict[str, dict[str, Any]] = {}


def r1a_lookup(
    *,
    interview_slug: str,
    briefing_hash: str = "",
    evidence_hash: str = "",
) -> dict[str, Any] | None:
    """Look up exact cache entry by composite digest.

    Args:
        interview_slug: The interview slug.
        briefing_hash: Hash of the uploaded briefing (if any).
        evidence_hash: Hash of the evidence contract.

    Returns:
        Cached result dict or None on miss.
    """
    key = _make_key(interview_slug, briefing_hash, evidence_hash)
    return _cache.get(key)


def r1a_store(
    *,
    interview_slug: str,
    briefing_hash: str = "",
    evidence_hash: str = "",
    result: dict[str, Any],
) -> None:
    """Store a result in the exact cache.

    Args:
        interview_slug: The interview slug.
        briefing_hash: Hash of the uploaded briefing.
        evidence_hash: Hash of the evidence contract.
        result: The result to cache.
    """
    key = _make_key(interview_slug, briefing_hash, evidence_hash)
    _cache[key] = dict(result)


def _make_key(slug: str, bhash: str, ehash: str) -> str:
    raw = f"{slug}:{bhash}:{ehash}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


__all__ = ["r1a_lookup", "r1a_store"]
