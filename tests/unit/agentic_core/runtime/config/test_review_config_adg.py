"""ADG importability contract for agentic_core/runtime/config/review_config.py."""
from __future__ import annotations

import agentic_core.runtime.config.review_config  # noqa: F401


def test_module_importable():
    """Module review_config must be importable."""
    assert agentic_core.runtime.config.review_config is not None
