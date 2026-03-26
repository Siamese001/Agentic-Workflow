"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.reasoning.CognitiveDispositionAgent  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.reasoning.CognitiveDispositionAgent  # noqa: F401
    """Module CognitiveDispositionAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.CognitiveDispositionAgent is not None
