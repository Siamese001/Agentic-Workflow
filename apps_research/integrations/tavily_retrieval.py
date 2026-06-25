"""Deprecated Tavily retrieval shim for apps_research.

apps_research product retrieval is SearXNG-only. This module remains only so
legacy imports fail loudly with an actionable error instead of silently
calling Tavily.
"""

from __future__ import annotations

from dataclasses import dataclass


def apply_contextual_prefix(
    chunk: str,
    *,
    doc_title: str = "",
    surrounding_text: str = "",
) -> str:
    """Wrap ``chunk`` with Anthropic contextual-retrieval template (plan §P4.5).

    Produces ``<document>{doc_title}</document>\\n<chunk_context>{surrounding_text}</chunk_context>\\n{chunk}``.
    Empty doc_title / surrounding_text render as empty tags (preserves
    template shape for grep-based audits).
    """
    return (
        f"<document>{doc_title}</document>\n"
        f"<chunk_context>{surrounding_text}</chunk_context>\n"
        f"{chunk}"
    )


@dataclass(frozen=True)
class RetrievedDoc:
    """A single Tavily search hit, normalized for downstream rerank."""

    url: str
    title: str
    snippet: str
    score: float


def retrieve(sub_query: str, top_k: int = 10) -> list[RetrievedDoc]:
    """Fail loudly: Tavily is no longer an apps_research provider."""
    raise RuntimeError(
        "apps_research Tavily retrieval is deprecated and disabled. "
        "Use the SearXNG product path with SEARXNG_BASE_URL / agentic_searxng."
    )
