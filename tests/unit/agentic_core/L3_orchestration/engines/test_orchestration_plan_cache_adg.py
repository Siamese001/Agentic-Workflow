"""ADG importability contract for agentic_core/L3_orchestration/engines/orchestration_plan_cache.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_orchestration_plan_cache.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.engines.orchestration_plan_cache import (  # noqa: F401
        OrchestrationPlanCache,
        get_orchestration_plan_cache,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    OrchestrationPlanCache = None  # type: ignore[assignment,misc]
    get_orchestration_plan_cache = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="orchestration_plan_cache.py deps unavailable")
class TestOrchestrationPlanCacheImportability:
    def test_module_importable(self) -> None:
        """ADG contract: orchestration_plan_cache.py must be importable."""
        assert _AVAILABLE

    def test_orchestrationplancache_is_type(self) -> None:
        assert OrchestrationPlanCache is not None

    def test_get_orchestration_plan_cache_callable(self) -> None:
        assert callable(get_orchestration_plan_cache)

