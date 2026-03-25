"""ADG importability contract for agentic_core/config/core/reflection_config.py."""
from __future__ import annotations

import agentic_core.config.core.reflection_config  # noqa: F401


def test_module_importable():
    """Module reflection_config must be importable."""
    assert agentic_core.config.core.reflection_config is not None
