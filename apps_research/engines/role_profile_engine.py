"""RoleProfileEngine — apps_research --mode role_profile (plan §P2.3).

Produces a RoleProfile dict conforming to
``apps_research.types.role_profile.RoleProfile``. Uses the V2 retrieval
pipeline (query decomposer -> SearXNG -> reranker) when ``SEARXNG_BASE_URL``
is set and ``APPS_RESEARCH_RETRIEVAL_V2=1``; otherwise returns a structured
stub so the pipeline stays green in offline environments.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict

_log = logging.getLogger(__name__)


_STUB_REQUIRED_SKILLS: list[str] = [
    "Python",
    "SQL",
    "ML fundamentals",
    "Stakeholder communication",
    "Production system design",
]

_STUB_NICE_TO_HAVE: list[str] = [
    "LLM ops",
    "Distributed systems",
    "Domain expertise",
]


def _v2_enabled() -> bool:
    return os.environ.get("APPS_RESEARCH_RETRIEVAL_V2", "").strip() in {
        "1",
        "true",
        "yes",
        "on",
    }


class RoleProfileEngine:
    """Generates a structured RoleProfile for a target role."""

    AGENT_ID = "apps_research.role_profile_engine"

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        role = str(payload.get("role") or payload.get("topic") or "").strip()
        if not role:
            raise ValueError("RoleProfileEngine requires non-empty 'role' (or 'topic')")
        depth = str(payload.get("depth", "standard"))

        sources: list[dict[str, str]] = []
        if _v2_enabled():
            sources = self._fetch_sources_v2(role=role, depth=depth)

        scope = (
            f"{role} is responsible for leading data strategy, managing "
            "cross-functional delivery, and driving measurable business "
            "outcomes through applied analytics and ML."
        )
        return {
            "role": role,
            "scope": scope,
            "required_skills": list(_STUB_REQUIRED_SKILLS),
            "nice_to_have": list(_STUB_NICE_TO_HAVE),
            "source_register": sources,
        }

    def _fetch_sources_v2(self, *, role: str, depth: str) -> list[dict[str, str]]:
        from apps_research.engines.query_decomposer import decompose
        from apps_research.integrations.reranker_adapter import rerank
        from apps_research.integrations.search_retrieval import retrieve

        depth_norm = depth if depth in {"shallow", "standard", "deep"} else "standard"
        try:
            sub_queries = decompose(role, depth=depth_norm)  # type: ignore[arg-type]
        except ValueError:
            return []
        sources: list[dict[str, str]] = []
        for sq in sub_queries:
            try:
                docs = retrieve(sq.text, top_k=10)
            except (RuntimeError, ValueError) as exc:
                _log.info("[RoleProfileEngine] retrieve skipped for %s: %s", sq.facet, exc)
                continue
            for d in rerank(sq.text, docs, cutoff=3):
                sources.append({"url": d.url, "title": d.title})
        return sources
