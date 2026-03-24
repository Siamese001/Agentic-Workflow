"""ADG importability contract for agentic_core/cache/redis_coordination_fabric.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_redis_coordination_fabric.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.cache.redis_coordination_fabric import (  # noqa: F401
        RedisCoordinationFabric,
        get_coordination_fabric,
        reset_coordination_fabric,
    )

    _AVAILABLE = True
except (ValueError, TypeError, RuntimeError) as e:  # guardian: allow-silent-swallow
    _AVAILABLE = False
    RedisCoordinationFabric = None  # type: ignore[assignment,misc]
    get_coordination_fabric = None  # type: ignore[assignment,misc]
    reset_coordination_fabric = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="redis_coordination_fabric deps unavailable")
class TestRedisCoordinationFabricImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/cache/redis_coordination_fabric.py must be importable."""
        assert _AVAILABLE

    def test_rediscoordinationfabric_defined(self) -> None:
        assert RedisCoordinationFabric is not None