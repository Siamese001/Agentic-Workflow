"""ADG importability contract for agentic_core/L3_orchestration/reasoning/SubAtomicAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L3_orchestration.reasoning.SubAtomicAgent  # noqa: F401


def test_module_importable():
        import agentic_core.L3_orchestration.reasoning.SubAtomicAgent  # noqa: F401
        """Module SubAtomicAgent must be importable."""
        assert agentic_core.L3_orchestration.reasoning.SubAtomicAgent is not None

    assert agentic_core.L3_orchestration.reasoning.SubAtomicAgent is not None
