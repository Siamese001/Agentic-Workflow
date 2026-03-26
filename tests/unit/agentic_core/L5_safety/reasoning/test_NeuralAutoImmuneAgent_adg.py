"""ADG importability contract for agentic_core/L5_safety/reasoning/NeuralAutoImmuneAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.reasoning.NeuralAutoImmuneAgent  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.reasoning.NeuralAutoImmuneAgent  # noqa: F401
        """Module NeuralAutoImmuneAgent must be importable."""
        assert agentic_core.L5_safety.reasoning.NeuralAutoImmuneAgent is not None

    assert agentic_core.L5_safety.reasoning.NeuralAutoImmuneAgent is not None
