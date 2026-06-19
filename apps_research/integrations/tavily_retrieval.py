"""Backward-compatible import wrapper for the legacy Tavily adapter name.

The active provider is SearXNG via ``apps_research.integrations.search_retrieval``.
This module remains only so older imports keep resolving while callers migrate
to the provider-neutral name.
"""

from __future__ import annotations

from apps_research.integrations.search_retrieval import (
    RetrievedDoc,
    apply_contextual_prefix,
    retrieve,
)

__all__ = ["RetrievedDoc", "apply_contextual_prefix", "retrieve"]
