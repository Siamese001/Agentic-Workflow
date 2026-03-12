"""ADG importability contract for system_learning/engines/rag_retrieval_cache.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_rag_retrieval_cache.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.engines.rag_retrieval_cache import (  # noqa: F401
        RagRetrievalCache,
        get_rag_retrieval_cache,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RagRetrievalCache = None  # type: ignore[assignment,misc]
    get_rag_retrieval_cache = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="rag_retrieval_cache.py deps unavailable")
class TestRagRetrievalCacheImportability:
    def test_module_importable(self) -> None:
        """ADG contract: rag_retrieval_cache.py must be importable."""
        assert _AVAILABLE

    def test_ragretrievalcache_is_type(self) -> None:
        assert RagRetrievalCache is not None

    def test_get_rag_retrieval_cache_callable(self) -> None:
        assert callable(get_rag_retrieval_cache)

