"""ADG importability contract for agentic_core/L3_orchestration/reasoning/DAGMutatorAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L3_orchestration.reasoning.DAGMutatorAgent  # noqa: F401


def test_module_importable():
        import agentic_core.L3_orchestration.reasoning.DAGMutatorAgent  # noqa: F401
        """Module DAGMutatorAgent must be importable."""
        assert agentic_core.L3_orchestration.reasoning.DAGMutatorAgent is not None

    assert agentic_core.L3_orchestration.reasoning.DAGMutatorAgent is not None
