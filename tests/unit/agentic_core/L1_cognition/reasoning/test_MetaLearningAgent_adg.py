"""ADG importability contract for agentic_core/L1_cognition/reasoning/MetaLearningAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L1_cognition.reasoning.MetaLearningAgent  # noqa: F401


def test_module_importable():
    import agentic_core.L1_cognition.reasoning.MetaLearningAgent  # noqa: F401
    """Module MetaLearningAgent must be importable."""
    assert agentic_core.L1_cognition.reasoning.MetaLearningAgent is not None
