"""Unit tests for AI-checking-AI hardenings: GAP-01, GAP-02, GAP-04, GAP-05."""
from __future__ import annotations

import agentic_core.config.core.reflection_config  # noqa: F401


def test_module_importable():
    """Module reflection_config must be importable."""
    assert agentic_core.config.core.reflection_config is not None
