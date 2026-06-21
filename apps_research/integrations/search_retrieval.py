"""Provider-neutral web retrieval adapter for apps_research.

SearXNG is the primary provider. It exposes a simple HTTP search API at
``/search`` and returns JSON when the instance enables the ``json`` format.
This module keeps the downstream retrieval contract stable while removing
Tavily SDK/vendor-key coupling from the active runtime path.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

import requests

_log = logging.getLogger("apps_research.search_retrieval")

_BASE_URL_ENV = "SEARXNG_BASE_URL"
_TIMEOUT_ENV = "SEARXNG_TIMEOUT_SECONDS"
_CATEGORIES_ENV = "SEARXNG_CATEGORIES"
_ENGINES_ENV = "SEARXNG_ENGINES"
_DEFAULT_TIMEOUT_SECONDS = 20.0


def apply_contextual_prefix(
    chunk: str,
    *,
    doc_title: str = "",
    surrounding_text: str = "",
) -> str:
    """Wrap ``chunk`` with the contextual-retrieval template used by PA tests."""
    return (
        f"<document>{doc_title}</document>\n"
        f"<chunk_context>{surrounding_text}</chunk_context>\n"
        f"{chunk}"
    )


@dataclass(frozen=True)
class RetrievedDoc:
    """A single web search hit, normalized for downstream rerank."""

    url: str
    title: str
    snippet: str
    score: float


def _require_base_url() -> str:
    base_url = os.environ.get(_BASE_URL_ENV, "").strip()
    if not base_url:
        raise RuntimeError(
            f"{_BASE_URL_ENV} is not set. "
            "Set it to your SearXNG instance base URL before calling "
            "apps_research.integrations.search_retrieval.retrieve(). "
            "The instance must enable JSON search output."
        )
    return base_url.rstrip("/")


def _timeout_seconds() -> float:
    raw = os.environ.get(_TIMEOUT_ENV, "").strip()
    if not raw:
        return _DEFAULT_TIMEOUT_SECONDS
    try:
        return max(1.0, float(raw))
    except ValueError as exc:
        raise RuntimeError(f"{_TIMEOUT_ENV} must be a numeric timeout in seconds") from exc


def _optional_csv_env(name: str) -> str | None:
    value = os.environ.get(name, "").strip()
    return value or None


def _coerce_score(hit: dict[str, Any], fallback: float) -> float:
    raw = hit.get("score")
    if raw is None:
        return fallback
    try:
        return float(raw)
    except (TypeError, ValueError):
        return fallback


def _normalize_results(payload: Any, *, top_k: int) -> list[RetrievedDoc]:
    results = payload.get("results", []) if isinstance(payload, dict) else []
    docs: list[RetrievedDoc] = []
    for index, hit in enumerate(results):
        if not isinstance(hit, dict):
            continue
        url = str(hit.get("url") or "").strip()
        if not url:
            continue
        title = str(hit.get("title") or url).strip()
        snippet = str(hit.get("content") or hit.get("snippet") or "").strip()
        fallback_score = max(0.0, 1.0 - (index * 0.01))
        docs.append(
            RetrievedDoc(
                url=url,
                title=title,
                snippet=snippet,
                score=_coerce_score(hit, fallback_score),
            )
        )
        if len(docs) >= top_k:
            break
    return docs


def retrieve(sub_query: str, top_k: int = 10) -> list[RetrievedDoc]:
    """Fetch up to ``top_k`` docs for ``sub_query`` from SearXNG.

    Raises:
        ValueError: if ``sub_query`` or ``top_k`` is invalid.
        RuntimeError: if SearXNG is not configured or the HTTP/API call fails.
    """
    query = (sub_query or "").strip()
    if not query:
        raise ValueError("sub_query must be non-empty")
    if top_k <= 0:
        raise ValueError("top_k must be positive")

    base_url = _require_base_url()
    params: dict[str, str | int] = {
        "q": query,
        "format": "json",
    }
    categories = _optional_csv_env(_CATEGORIES_ENV)
    engines = _optional_csv_env(_ENGINES_ENV)
    if categories:
        params["categories"] = categories
    if engines:
        params["engines"] = engines

    url = f"{base_url}/search"
    try:
        response = requests.get(url, params=params, timeout=_timeout_seconds())
        response.raise_for_status()
        payload = response.json()
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "unknown"
        if status_code == 403:
            raise RuntimeError(
                "SearXNG returned 403. Confirm the instance enables JSON output "
                "for search.format=json."
            ) from exc
        raise RuntimeError(f"SearXNG search failed with HTTP status {status_code}") from exc
    except requests.RequestException as exc:
        raise RuntimeError(f"SearXNG search request failed: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError("SearXNG search response was not valid JSON") from exc

    docs = _normalize_results(payload, top_k=top_k)
    _log.info("[searxng] sub_query=%r returned %d docs", query, len(docs))
    return docs


__all__ = ["RetrievedDoc", "apply_contextual_prefix", "retrieve"]
