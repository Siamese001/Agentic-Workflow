"""ADG importability contract for agentic_core/L3_orchestration/engines/rl_coordinator_orchestrator.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L3_orchestration.engines.rl_coordinator_orchestrator  # noqa: F401


def test_module_importable():
    import agentic_core.L3_orchestration.engines.rl_coordinator_orchestrator  # noqa: F401
    """Module rl_coordinator_orchestrator must be importable."""
    assert agentic_core.L3_orchestration.engines.rl_coordinator_orchestrator is not None
