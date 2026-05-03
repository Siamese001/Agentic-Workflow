"""Tavily retrieval adapter for apps_research.

Plan §P1.2 — reads ``TAVILY_API_KEY`` from env, surfaces graceful error
when absent (no silent fallback). Uses the ``tavily-python`` SDK
(already a project dep via the tavily MCP installation).

Remote MCP serialization (constitutional §25) is a Cascade-side concern;
this module is library-level and may be called from any hot path.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass

_log = logging.getLogger("apps_research.tavily_retrieval")

_ENV_VAR = "TAVILY_API_KEY"


@dataclass(frozen=True)
class RetrievedDoc:
    """A single Tavily search hit, normalized for downstream rerank."""

    url: str
    title: str
    snippet: str
    score: float


def _require_api_key() -> str:
    key = os.environ.get(_ENV_VAR, "").strip()
    if not key:
        raise RuntimeError(
            f"{_ENV_VAR} is not set. "
            "Set it in your environment or .env file before calling "
            "apps_research.integrations.tavily_retrieval.retrieve(). "
            "See .env.example for the canonical entry."
        )
    return key


def retrieve(sub_query: str, top_k: int = 10) -> list[RetrievedDoc]:
    """Fetch up to ``top_k`` docs for ``sub_query`` from Tavily.

    Args:
        sub_query: a single decomposed sub-query string.
        top_k: maximum results (default 10 per plan P1.2 acceptance).

    Returns:
        List of :class:`RetrievedDoc`, never None. May return fewer than
        ``top_k`` when Tavily returns fewer hits.

    Raises:
        RuntimeError: if ``TAVILY_API_KEY`` is unset or the Tavily SDK
            is not installed.
    """
    if not (sub_query or "").strip():
        raise ValueError("sub_query must be non-empty")
    api_key = _require_api_key()

    try:
        from tavily import TavilyClient  # type: ignore[import-untyped]
    except ImportError as exc:
        raise RuntimeError(
            "tavily-python SDK not installed. "
            "Install via: pip install tavily-python"
        ) from exc

    client = TavilyClient(api_key=api_key)
    resp = client.search(
        query=sub_query,
        max_results=top_k,
        search_depth="advanced",
    )
    results = resp.get("results", []) if isinstance(resp, dict) else []
    docs: list[RetrievedDoc] = []
    for hit in results:
        if not isinstance(hit, dict):
            continue
        docs.append(
            RetrievedDoc(
                url=str(hit.get("url", "")),
                title=str(hit.get("title", "")),
                snippet=str(hit.get("content", "")),
                score=float(hit.get("score", 0.0)),
            )
        )
    _log.info("[tavily] sub_query=%r returned %d docs", sub_query, len(docs))
    return docs
