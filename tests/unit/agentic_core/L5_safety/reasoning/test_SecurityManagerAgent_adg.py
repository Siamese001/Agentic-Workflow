"""ADG importability contract for agentic_core/L5_safety/reasoning/SecurityManagerAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.reasoning.SecurityManagerAgent  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.reasoning.SecurityManagerAgent  # noqa: F401
        """Module SecurityManagerAgent must be importable."""
        assert agentic_core.L5_safety.reasoning.SecurityManagerAgent is not None

    assert agentic_core.L5_safety.reasoning.SecurityManagerAgent is not None
