"""ADG importability contract for agentic_core/L1_cognition/engines/CognitiveNode.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L1_cognition.engines.CognitiveNode  # noqa: F401


def test_module_importable():
        import agentic_core.L1_cognition.engines.CognitiveNode  # noqa: F401
        """Module CognitiveNode must be importable."""
        assert agentic_core.L1_cognition.engines.CognitiveNode is not None

    assert agentic_core.L1_cognition.engines.CognitiveNode is not None
