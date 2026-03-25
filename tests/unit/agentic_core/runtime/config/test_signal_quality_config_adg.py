"""ADG importability contract for agentic_core/runtime/config/signal_quality_config.py."""
from __future__ import annotations

import agentic_core.runtime.config.signal_quality_config  # noqa: F401


def test_module_importable():
    """Module signal_quality_config must be importable."""
    assert agentic_core.runtime.config.signal_quality_config is not None
