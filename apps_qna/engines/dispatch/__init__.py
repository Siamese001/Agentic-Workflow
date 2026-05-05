"""apps_qna.engines.dispatch — provider dispatch layer for apps_qna.

Plan: ``.windsurf/plans/bge-m3-deferred-scope-remaining-c4e7a1.md`` W3

Routes apps_qna queries to the appropriate LLM provider based on query type.
"""

from __future__ import annotations

from .provider_dispatch import DispatchResult, ProviderDispatcher, dispatch

__all__ = ["DispatchResult", "ProviderDispatcher", "dispatch"]
