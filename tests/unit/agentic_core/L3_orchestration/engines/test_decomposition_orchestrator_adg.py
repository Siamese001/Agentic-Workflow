"""ADG importability contract for agentic_core/L3_orchestration/engines/decomposition_orchestrator.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L3_orchestration.engines.decomposition_orchestrator  # noqa: F401


def test_module_importable():
        import agentic_core.L3_orchestration.engines.decomposition_orchestrator  # noqa: F401
        """Module decomposition_orchestrator must be importable."""
        assert agentic_core.L3_orchestration.engines.decomposition_orchestrator is not None

    assert agentic_core.L3_orchestration.engines.decomposition_orchestrator is not None
