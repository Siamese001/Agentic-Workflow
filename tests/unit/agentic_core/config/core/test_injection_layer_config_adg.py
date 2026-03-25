"""ADG importability contract for agentic_core/config/core/injection_layer_config.py."""
from __future__ import annotations

import agentic_core.config.core.injection_layer_config  # noqa: F401


def test_module_importable():
    """Module injection_layer_config must be importable."""
    assert agentic_core.config.core.injection_layer_config is not None
