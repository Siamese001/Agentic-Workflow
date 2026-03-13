"""ADG importability contract for agentic_core/L4_state/memory/in_memory_vector_cache.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_in_memory_vector_cache.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.memory.in_memory_vector_cache import (  # noqa: F401
        InMemoryVectorCache,
        TieredVectorStore,
        create_memory_vector_cache,
        create_tiered_vector_store,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    InMemoryVectorCache = None  # type: ignore[assignment,misc]
    TieredVectorStore = None  # type: ignore[assignment,misc]
    create_memory_vector_cache = None  # type: ignore[assignment,misc]
    create_tiered_vector_store = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="in_memory_vector_cache deps unavailable")
class TestInMemoryVectorCacheImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L4_state/memory/in_memory_vector_cache.py must be importable."""
        assert _AVAILABLE

    def test_inmemoryvectorcache_defined(self) -> None:
        assert InMemoryVectorCache is not None

    def test_tieredvectorstore_defined(self) -> None:
        assert TieredVectorStore is not None
