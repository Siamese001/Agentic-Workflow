"""Compatibility tests for the legacy tavily_retrieval module name."""

from __future__ import annotations

from apps_research.integrations import search_retrieval, tavily_retrieval


def test_legacy_module_reexports_retrieval_contract():
    assert tavily_retrieval.RetrievedDoc is search_retrieval.RetrievedDoc
    assert tavily_retrieval.apply_contextual_prefix is search_retrieval.apply_contextual_prefix
    assert tavily_retrieval.retrieve is search_retrieval.retrieve
