"""ADG importability contract for agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.reasoning.CodeEnforcerAgent  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.reasoning.CodeEnforcerAgent  # noqa: F401
        """Module CodeEnforcerAgent must be importable."""
        assert agentic_core.L5_safety.reasoning.CodeEnforcerAgent is not None

    assert agentic_core.L5_safety.reasoning.CodeEnforcerAgent is not None
