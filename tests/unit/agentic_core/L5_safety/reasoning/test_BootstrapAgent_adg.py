"""ADG importability contract for agentic_core/L5_safety/reasoning/BootstrapAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.reasoning.BootstrapAgent  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.reasoning.BootstrapAgent  # noqa: F401
        """Module BootstrapAgent must be importable."""
        assert agentic_core.L5_safety.reasoning.BootstrapAgent is not None

    assert agentic_core.L5_safety.reasoning.BootstrapAgent is not None
