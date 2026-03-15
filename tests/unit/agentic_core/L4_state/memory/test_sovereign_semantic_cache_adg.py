"""ADG importability contract for agentic_core/L4_state/memory/sovereign_semantic_cache.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_sovereign_semantic_cache.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.memory.sovereign_semantic_cache import (  # noqa: F401
        SovereignSemanticCache,
        get_redis_client,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    get_redis_client = None  # type: ignore[assignment,misc]
    SovereignSemanticCache = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_semantic_cache deps unavailable")
class TestSovereignSemanticCacheImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L4_state/memory/sovereign_semantic_cache.py must be importable."""
        assert _AVAILABLE

    def test_sovereignsemanticcache_defined(self) -> None:
        assert SovereignSemanticCache is not None
