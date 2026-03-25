"""ADG importability contract for agentic_core/L3_orchestration/engines/sovereign_redis_orchestrator.py."""
from __future__ import annotations

import agentic_core.L3_orchestration.engines.sovereign_redis_orchestrator  # noqa: F401


def test_module_importable():
    """Module sovereign_redis_orchestrator must be importable."""
    assert agentic_core.L3_orchestration.engines.sovereign_redis_orchestrator is not None
