"""ADG importability contract for agentic_core/runtime/config/model_provider_config.py."""
from __future__ import annotations

import agentic_core.runtime.config.model_provider_config  # noqa: F401


def test_module_importable():
    """Module model_provider_config must be importable."""
    assert agentic_core.runtime.config.model_provider_config is not None
