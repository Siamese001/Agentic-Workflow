"""ADG importability contract for agentic_core/L5_safety/reasoning/CodeHealerAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.reasoning.CodeHealerAgent  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.reasoning.CodeHealerAgent  # noqa: F401
        """Module CodeHealerAgent must be importable."""
        assert agentic_core.L5_safety.reasoning.CodeHealerAgent is not None

    assert agentic_core.L5_safety.reasoning.CodeHealerAgent is not None
