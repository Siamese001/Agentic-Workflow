"""ADG importability contract for system_learning/engines/rag_retrieval_cache.py."""
from __future__ import annotations

import system_learning.engines.rag_retrieval_cache  # noqa: F401


def test_module_importable():
    """Module rag_retrieval_cache must be importable."""
    assert system_learning.engines.rag_retrieval_cache is not None
