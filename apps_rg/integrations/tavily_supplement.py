"""Tavily supplement adapter — fills null and stale fields in a CompanyBrief
without producing one from scratch. Per locked decision D3/D4: opt-in via
--auto-research-tavily, fail-soft (never aborts pipeline).

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md (P6.3).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from apps_rg.types.company_research import CompanyBrief

_log = logging.getLogger(__name__)

# Fields eligible for supplement when null/empty. (Author-Gate W6.3 surface.)
_SUPPLEMENTABLE = {
    "tagline": "{company} company tagline",
    "core_offerings": "{company} core service offerings",
    "tech_stack_signals": "{company} technology stack",
    "cultural_cues": "{company} culture values",
    "leadership": "{company} leadership team executives",
    "competitive_set": "{company} competitors",
    "pain_points_inferred": "{company} customer challenges 2025",
    "recent_moves": "{company} news 2025 announcements",
}


def supplement_company_brief(brief: CompanyBrief) -> CompanyBrief:
    """Best-effort supplement.

    Returns the same brief on any failure. Caller treats as fail-soft.
    """
    try:
        client = _get_tavily_client()
    except RuntimeError as exc:
        _log.info("[tavily_supplement] Tavily unavailable: %s", exc)
        return brief

    updates: Dict[str, Any] = {}
    company = brief.company

    # tagline
    if not brief.overview.tagline or brief.overview.tagline.startswith("(stub"):
        snippet = _safe_search(client, _SUPPLEMENTABLE["tagline"].format(company=company))
        if snippet:
            updates["overview"] = brief.overview.model_copy(update={"tagline": snippet[:200]})

    # core_offerings
    if not brief.overview.core_offerings:
        items = _safe_search_list(client, _SUPPLEMENTABLE["core_offerings"].format(company=company))
        if items:
            ov = updates.get("overview", brief.overview)
            updates["overview"] = ov.model_copy(update={"core_offerings": items[:5]})

    for field_name in ("tech_stack_signals", "cultural_cues", "competitive_set", "pain_points_inferred"):
        if not getattr(brief, field_name):
            items = _safe_search_list(client, _SUPPLEMENTABLE[field_name].format(company=company))
            if items:
                updates[field_name] = items[:8]

    if not updates:
        return brief

    try:
        # Re-stamp fetched_at because the brief was modified.
        updates["fetched_at"] = datetime.now(timezone.utc)
        return brief.model_copy(update=updates)
    except Exception as exc:  # guardian: allow-broad-exception -- pydantic copy raises heterogeneous; fail-soft preserves the original brief
        _log.warning("[tavily_supplement] could not apply updates: %s", exc)
        return brief


def _get_tavily_client():
    try:
        from tools.retrieval.tavily_client import TavilySearchClient  # type: ignore
    except ImportError as exc:
        raise RuntimeError(f"Tavily client import failed: {exc}") from exc
    try:
        return TavilySearchClient()
    except Exception as exc:  # guardian: allow-broad-exception -- Tavily init heterogeneous (auth/HTTP/missing-key); surface as plain runtime error
        raise RuntimeError(f"Tavily client init failed: {exc}") from exc


def _safe_search(client, query: str) -> Optional[str]:
    try:
        resp = client.search(query=query, max_results=3)
    except Exception as exc:  # guardian: allow-broad-exception -- Tavily HTTP errors heterogeneous; per-query fail-soft preserves remaining supplements
        _log.info("[tavily_supplement] query failed (%s): %s", query, exc)
        return None
    results = (resp or {}).get("results", []) or []
    for r in results:
        text = r.get("content") or r.get("snippet") or ""
        if text:
            return text.strip()
    return None


def _safe_search_list(client, query: str) -> List[str]:
    """Return a deduplicated list of candidate strings extracted from Tavily snippets."""
    try:
        resp = client.search(query=query, max_results=5)
    except Exception as exc:  # guardian: allow-broad-exception -- Tavily HTTP errors heterogeneous; per-query fail-soft
        _log.info("[tavily_supplement] list-query failed (%s): %s", query, exc)
        return []

    bag: List[str] = []
    seen: set[str] = set()
    for r in (resp or {}).get("results", []) or []:
        text = (r.get("content") or r.get("snippet") or "").strip()
        if not text:
            continue
        # Heuristic split — pull comma- or bullet-delimited fragments.
        for frag in _split_fragments(text):
            norm = frag.strip().lower()
            if 3 <= len(frag) <= 80 and norm not in seen:
                seen.add(norm)
                bag.append(frag.strip())
    return bag


def _split_fragments(text: str) -> List[str]:
    out: List[str] = []
    for line in text.splitlines():
        line = line.strip(" -*•·")
        if not line:
            continue
        for part in line.split(","):
            p = part.strip()
            if p:
                out.append(p)
    return out


__all__ = ["supplement_company_brief"]
