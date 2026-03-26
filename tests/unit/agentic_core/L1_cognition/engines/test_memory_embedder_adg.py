"""ADG-driven tests for L1_cognition/engines/memory_embedder.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L1_cognition.engines.memory_embedder  # noqa: F401


def test_module_importable():
    import agentic_core.L1_cognition.engines.memory_embedder  # noqa: F401
    """Module memory_embedder must be importable."""
    assert agentic_core.L1_cognition.engines.memory_embedder is not None
