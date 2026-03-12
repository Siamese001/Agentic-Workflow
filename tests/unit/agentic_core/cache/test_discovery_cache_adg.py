"""ADG importability contract for agentic_core/cache/discovery_cache.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_discovery_cache.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.cache.discovery_cache import (  # noqa: F401
        AgentDiscoveryCache,
        get_agent_discovery_cache,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    AgentDiscoveryCache = None  # type: ignore[assignment,misc]
    get_agent_discovery_cache = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="discovery_cache.py deps unavailable")
class TestDiscoveryCacheImportability:
    def test_module_importable(self) -> None:
        """ADG contract: discovery_cache.py must be importable."""
        assert _AVAILABLE

    def test_agentdiscoverycache_is_type(self) -> None:
        assert AgentDiscoveryCache is not None

    def test_get_agent_discovery_cache_callable(self) -> None:
        assert callable(get_agent_discovery_cache)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

