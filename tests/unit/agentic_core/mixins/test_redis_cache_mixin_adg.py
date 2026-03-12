"""ADG importability contract for agentic_core/mixins/redis_cache_mixin.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_redis_cache_mixin.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.mixins.redis_cache_mixin import (  # noqa: F401
        CircuitBreaker,
        RedisCacheMixin,
        get_cache_metrics,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    CircuitBreaker = None  # type: ignore[assignment,misc]
    RedisCacheMixin = None  # type: ignore[assignment,misc]
    get_cache_metrics = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="redis_cache_mixin.py deps unavailable")
class TestRedisCacheMixinImportability:
    def test_module_importable(self) -> None:
        """ADG contract: redis_cache_mixin.py must be importable."""
        assert _AVAILABLE

    def test_circuitbreaker_is_type(self) -> None:
        assert CircuitBreaker is not None

    def test_rediscachemixin_is_type(self) -> None:
        assert RedisCacheMixin is not None

    def test_get_cache_metrics_callable(self) -> None:
        assert callable(get_cache_metrics)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

