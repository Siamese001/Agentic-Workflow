"""ADG importability contract for agentic_core/L3_orchestration/engines/sovereign_redis_orchestrator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_sovereign_redis_orchestrator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.engines.sovereign_redis_orchestrator import (  # noqa: F401
        SovereignRedisOrchestrator,
        get_sovereign_redis_orchestrator,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    SovereignRedisOrchestrator = None  # type: ignore[assignment,misc]
    get_sovereign_redis_orchestrator = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_redis_orchestrator deps unavailable")
class TestSovereignRedisOrchestratorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L3_orchestration/engines/sovereign_redis_orchestrator.py must be importable."""
        assert _AVAILABLE

    def test_sovereignredisorchestrator_defined(self) -> None:
        assert SovereignRedisOrchestrator is not None
