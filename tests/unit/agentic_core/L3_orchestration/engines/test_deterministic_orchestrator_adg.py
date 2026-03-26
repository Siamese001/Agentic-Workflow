"""ADG importability contract for agentic_core/L3_orchestration/engines/deterministic_orchestrator.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L3_orchestration.engines.deterministic_orchestrator  # noqa: F401


def test_module_importable():
    import agentic_core.L3_orchestration.engines.deterministic_orchestrator  # noqa: F401
    """Module deterministic_orchestrator must be importable."""
    assert agentic_core.L3_orchestration.engines.deterministic_orchestrator is not None
